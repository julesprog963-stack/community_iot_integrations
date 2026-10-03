from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class CommunityIotZplDevice(models.Model):
    _inherit = "community_iot_box.iot_device"

    zpl_width_mm = fields.Float(string="Label Width (mm)", default=100.0)
    zpl_height_mm = fields.Float(string="Label Height (mm)", default=50.0)
    zpl_dpi = fields.Selection(
        [("203", "203 DPI"), ("300", "300 DPI"), ("600", "600 DPI")],
        string="ZPL DPI",
        default="203",
    )

    def action_zpl_test_label(self):
        self.ensure_one()
        self._check_zpl_access()
        zpl = (
            "^XA\n"
            "^CI28\n"
            "^FO30,30^A0N,32,32^FDJDA SOLUTIONS^FS\n"
            "^FO30,75^A0N,26,26^FDCommunity IoT ZPL^FS\n"
            "^FO30,115^BY2^BCN,60,Y,N,N^FDTEST-IOT-ZPL^FS\n"
            "^XZ\n"
        )
        job = self.env["community_iot_box.iot_job"]._create_zpl_jobs(
            device=self,
            zpl=zpl,
            name=_("ZPL test label - %(device)s", device=self.name),
        )
        return self._zpl_notify(_("ZPL test"), _("Queued job #%(job)s.", job=job[0].id), "success")

    def _check_zpl_access(self):
        if not self.env.user.has_group("community_iot_zpl.group_community_iot_zpl_user"):
            raise AccessError(_("You are not allowed to use Community IoT ZPL."))
        if (
            not self.active
            or self.type != "label_printer"
            or not self.box_id
            or self.box_id.company_id != self.env.company
            or self.box_id.state != "online"
            or not self.box_id.supports_capability("zpl_print_v1")
        ):
            raise ValidationError(_("Select an online label printer with ZPL support."))

    def _zpl_notify(self, title, message, level="info"):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": title, "message": message, "type": level, "sticky": False},
        }


class CommunityIotZplWizard(models.TransientModel):
    _name = "community.iot.zpl.wizard"
    _description = "Community IoT ZPL Print"

    company_id = fields.Many2one("res.company", required=True, readonly=True, default=lambda self: self.env.company)
    device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="ZPL Printer",
        required=True,
        domain="[('type', '=', 'label_printer'), ('active', '=', True), ('box_id.company_id', '=', company_id), ('box_id.state', '=', 'online')]",
    )
    name = fields.Char(required=True, default="Community IoT ZPL Label")
    zpl = fields.Text(required=True, string="ZPL")
    copies = fields.Integer(default=1, required=True)

    @api.constrains("copies")
    def _check_copies(self):
        for wizard in self:
            if not 1 <= wizard.copies <= 10:
                raise ValidationError(_("Copies must be between 1 and 10."))

    def action_print(self):
        self.ensure_one()
        if not self.env.user.has_group("community_iot_zpl.group_community_iot_zpl_user"):
            raise AccessError(_("You are not allowed to use Community IoT ZPL."))
        self.device_id._check_zpl_access()
        jobs = self.env["community_iot_box.iot_job"]._create_zpl_jobs(
            device=self.device_id,
            zpl=self.zpl,
            name=self.name,
            copies=self.copies,
            origin_model=self._name,
            origin_id=self.id,
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("IoT ZPL"),
                "message": _("Queued %(count)s label job(s).", count=len(jobs)),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
