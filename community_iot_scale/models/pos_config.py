from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    community_iot_scale_device_id = fields.Many2one(
        "community_iot_box.iot_device",
        string="Community IoT Scale",
        domain="[('type', '=', 'scale'), ('active', '=', True), ('box_id.company_id', '=', company_id)]",
    )
    community_iot_scale_manual_confirm = fields.Boolean(
        string="Require manual weight confirmation",
        default=True,
        help="Read the scale and let the cashier confirm before changing a weighted product line.",
    )
