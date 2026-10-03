from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _get_pos_ui_pos_config(self, params):
        config = super()._get_pos_ui_pos_config(params)
        device = self.config_id.community_iot_scale_device_id
        config.update(
            {
                "community_iot_scale_device_id": device.id or False,
                "community_iot_scale_manual_confirm": self.config_id.community_iot_scale_manual_confirm,
                "community_iot_scale_unit": device.scale_unit if device else False,
            }
        )
        return config
