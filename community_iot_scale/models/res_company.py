from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    community_iot_scale_device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="Default IoT Scale",
        domain="[('type', '=', 'scale'), ('active', '=', True), ('box_id.company_id', '=', id)]",
    )
