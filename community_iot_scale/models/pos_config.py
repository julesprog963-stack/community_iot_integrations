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
    community_iot_scale_unit = fields.Char(
        string="Community IoT Scale Unit",
        compute="_compute_community_iot_scale_unit",
    )

    @api.depends("community_iot_scale_device_id", "community_iot_scale_device_id.scale_unit")
    def _compute_community_iot_scale_unit(self):
        for config in self:
            config.community_iot_scale_unit = config.community_iot_scale_device_id.scale_unit or False

    @api.model
    def _load_pos_data_fields(self, config):
        fields_list = super()._load_pos_data_fields(config)
        return fields_list + [
            "community_iot_scale_device_id",
            "community_iot_scale_manual_confirm",
            "community_iot_scale_unit",
        ]

    @api.model
    def _load_pos_data_read(self, records, config):
        read_records = super()._load_pos_data_read(records, config)
        if not read_records:
            return read_records
        device = config.community_iot_scale_device_id
        read_records[0].update(
            {
                "community_iot_scale_device_id": device.id or False,
            }
        )
        return read_records
