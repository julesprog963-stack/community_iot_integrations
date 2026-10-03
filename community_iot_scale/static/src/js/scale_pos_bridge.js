/** @odoo-module **/

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

export class CommunityIotScaleButton extends Component {
    static template = "community_iot_scale.ScaleButton";

    setup() {
        this.pos = usePos();
        this.orm = useService("orm");
        this.notification = useService("pos_notification");
    }

    get scaleUnit() {
        return this.pos.config.community_iot_scale_unit || "kg";
    }

    async readScale() {
        const deviceId = this.pos.config.community_iot_scale_device_id;
        if (!deviceId) {
            return;
        }
        try {
            const reading = await this.orm.call(
                "community_iot_box.iot_device",
                "get_latest_scale_reading",
                [deviceId]
            );
            const weight = Number(reading.weight || 0);
            const message = `Peso: ${weight} ${reading.unit || this.scaleUnit}`;
            if (!reading.stable) {
                this.notification.add(`${message} (inestable)`, { type: "warning" });
                return;
            }
            const line = this.pos.get_order()?.get_selected_orderline();
            if (
                line &&
                this.pos.config.community_iot_scale_manual_confirm &&
                window.confirm(`${message}. ¿Aplicar como cantidad?`)
            ) {
                line.set_quantity(weight);
            } else {
                this.notification.add(message, { type: "info" });
            }
        } catch (error) {
            console.warn("Community IoT scale read failed.", error);
            this.notification.add("No se pudo leer la báscula IoT.", { type: "danger" });
        }
    }
}

ProductScreen.addControlButton({
    component: CommunityIotScaleButton,
    condition() {
        return Boolean(this.pos.config.community_iot_scale_device_id);
    },
});
