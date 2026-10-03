# Community IoT Integrations

Addons opcionales para la suite Community IoT:

- `community_iot_zpl`: etiquetas ZPL para impresoras Zebra.
- `community_iot_scale`: lectura, tara, cero y lectura disponible para POS.

Cada rama del repositorio corresponde a una versión de Odoo: `17.0`, `18.0`
y `19.0`. Los addons dependen de `community_iot_box` de la misma versión.

El agente debe anunciar `zpl_print_v1` para etiquetas y `scale_read_v1` /
`scale_control_v1` para básculas. Los emuladores permanecen en el repositorio
del agente como herramientas de desarrollo y no se empaquetan aquí.
