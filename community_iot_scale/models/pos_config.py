from odoo import api, fields, models


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

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_list = super()._load_pos_data_fields(config_id)
        return fields_list + [
            "community_iot_scale_device_id",
            "community_iot_scale_manual_confirm",
        ]

    def _load_pos_data(self, data):
        payload = super()._load_pos_data(data)
        if not payload.get("data"):
            return payload
        config_id = data["pos.session"]["data"][0]["config_id"]
        config = self.browse(config_id).exists()
        device = config.community_iot_scale_device_id if config else self.env["community_iot_box.iot_device"]
        payload["data"][0].update(
            {
                "community_iot_scale_device_id": device.id or False,
                "community_iot_scale_unit": device.scale_unit if device else False,
            }
        )
        payload["fields"].append("community_iot_scale_unit")
        return payload
