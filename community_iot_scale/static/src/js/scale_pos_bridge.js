/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { ControlButtons } from "@point_of_sale/app/screens/product_screen/control_buttons/control_buttons";

patch(ControlButtons.prototype, {
    setup() {
        super.setup(...arguments);
        this.orm = useService("orm");
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
            const order = this.pos.getOrder();
            const line = order?.getSelectedOrderline();
            if (
                line &&
                this.pos.config.community_iot_scale_manual_confirm &&
                window.confirm(`${message}. ¿Aplicar como cantidad?`)
            ) {
                line.setQuantity(weight);
            } else {
                this.notification.add(message, { type: "info" });
            }
        } catch (error) {
            console.warn("Community IoT scale read failed.", error);
            this.notification.add("No se pudo leer la báscula IoT.", { type: "danger" });
        }
    }
});
