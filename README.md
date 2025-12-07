# Control de Humedad en Cava de Vinos 

Sistema de control automático de humedad relativa para cavas de vino utilizando un compensador PI.

## 📋 Descripción

Este proyecto implementa el diseño, análisis y simulación de un sistema de control de humedad relativa para una cava de vinos climatizada. El sistema mantiene la humedad dentro del rango óptimo de 65-75% HR, fundamental para la correcta conservación del vino.

**Trabajo Final Integrador** - Sistemas de Control I  
Universidad Nacional de Córdoba - Facultad de Ciencias Exactas, Físicas y Naturales

## 🎯 Objetivos del Sistema

- Mantener la humedad relativa en ~70% HR
- Eliminar el error en estado estable
- Reducir el tiempo de establecimiento
- Evitar sobrepasamiento (SO = 0%)
- Garantizar estabilidad robusta

## 🔧 Componentes del Sistema

### Hardware de Referencia
- **Humidificador**: Módulo ultrasónico (ref. WAS-2B02EN de Holtek)
  - Tasa de atomización: >200 mL/h
  - Control: 0-5V (modo VR)
- **Sensor**: HIH-4030
  - Sensibilidad: 30 mV/%HR
  - Tiempo de respuesta: τ = 5s
- **Recinto**: Cava para 28 botellas
  - Dimensiones: 80×50×50 cm (0.2 m³)

## 📊 Resultados del Diseño

### Sistema sin Compensar
- Tiempo de establecimiento: ~135s
- Error en estado estable: 50%
- Sistema tipo 0

### Sistema Compensado
- Tiempo de establecimiento: Mejorado significativamente
- Error en estado estable: 0% (sistema tipo 1)
- Margen de ganancia: 22.6 dB
- Margen de fase: ~73°
- Sobrepasamiento: 0%

## 👨‍🎓 Autor

**Gastón Capdevila**

---

**Universidad Nacional de Córdoba**  
Facultad de Ciencias Exactas, Físicas y Naturales  
2025
