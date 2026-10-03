from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class CommunityIotScaleDevice(models.Model):
    _inherit = "community_iot_box.iot_device"

    scale_live_enabled = fields.Boolean(string="Live POS Scale", default=True)

    def _check_scale_access(self, control=False):
        if not self.env.user.has_group("community_iot_scale.group_community_iot_scale_user"):
            raise AccessError(_("You are not allowed to use Community IoT Scale."))
        capability = "scale_control_v1" if control else "scale_read_v1"
        for device in self:
            if (
                not device.active
                or device.type != "scale"
                or not device.box_id
                or device.box_id.company_id != self.env.company
                or device.box_id.state != "online"
                or not device.box_id.supports_capability(capability)
            ):
                raise ValidationError(_("Select an online scale with the required agent capability."))

    def action_scale_read_once(self):
        self.ensure_one()
        self._check_scale_access()
        job = self.env["community_iot_box.iot_job"]._create_scale_job(
            device=self,
            job_type="scale_read_once",
            name=_("Read scale - %(device)s", device=self.name),
        )
        return self._scale_notify(_("Scale reading"), _("Queued job #%(job)s.", job=job.id), "success")

    def action_scale_zero(self):
        self.ensure_one()
        self._check_scale_access(control=True)
        job = self.env["community_iot_box.iot_job"]._create_scale_job(
            device=self,
            job_type="scale_zero",
            name=_("Zero scale - %(device)s", device=self.name),
        )
        return self._scale_notify(_("Scale zero"), _("Queued job #%(job)s.", job=job.id), "success")

    def action_scale_tare(self):
        self.ensure_one()
        self._check_scale_access(control=True)
        job = self.env["community_iot_box.iot_job"]._create_scale_job(
            device=self,
            job_type="scale_tare",
            name=_("Tare scale - %(device)s", device=self.name),
        )
        return self._scale_notify(_("Scale tare"), _("Queued job #%(job)s.", job=job.id), "success")

    @api.model
    def get_latest_scale_reading(self, device_id):
        if not self.env.user.has_group("community_iot_scale.group_community_iot_scale_user"):
            raise AccessError(_("You are not allowed to read Community IoT Scale data."))
        device = self.browse(device_id).exists()
        if not device or device.type != "scale" or device.box_id.company_id != self.env.company:
            raise ValidationError(_("The selected scale is not available."))
        return {
            "device_id": device.id,
            "device_key": device.device_key,
            "weight": device.last_weight,
            "unit": device.last_weight_unit or device.scale_unit or "kg",
            "stable": device.last_weight_stable,
            "zero": device.last_weight_zero,
            "tare": device.last_weight_tare,
            "sequence": device.last_weight_sequence,
            "timestamp": fields.Datetime.to_string(device.last_weight_at) if device.last_weight_at else False,
        }

    def _scale_notify(self, title, message, level="info"):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": title, "message": message, "type": level, "sticky": False},
        }
