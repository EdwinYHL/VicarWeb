# 🚗 VICAR - Sistema de Gestión de Flotas Vehiculares

**VICAR** es una aplicación web desarrollada con **Flask** y **PostgreSQL** para la gestión integral de flotas de vehículos, conductores, rentas, mantenimientos y reportes financieros. Está diseñada para funcionar en una **red local (intranet)** sin necesidad de conexión a internet externa, ideal para empresas de transporte y renta de vehículos.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-blue)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Características principales

- ✅ **Autenticación segura** con contraseñas cifradas (bcrypt).
- ✅ **CRUD completo** de vehículos, conductores, rentas y mantenimientos.
- ✅ **Control de disponibilidad**: los vehículos cambian automáticamente a "Rentado" al asignar una renta y vuelven a "Disponible" al finalizarla.
- ✅ **Registro de ingresos** por rentas y **egresos** por mantenimientos.
- ✅ **Generación de reportes** en HTML, Excel y PDF con filtro por fechas.
- ✅ **Gráficos interactivos** con Chart.js para visualizar balances.
- ✅ **Interfaz responsive** con Bootstrap 5.
- ✅ **Arquitectura cliente-servidor** para red local.
- ✅ **Base de datos PostgreSQL** instalada en el servidor local (sin dependencia de internet).

---

## 🖥️ Tecnologías utilizadas

| Capa          | Tecnología                         |
|---------------|------------------------------------|
| Backend       | Python 3.10+, Flask, Flask-Login   |
| Base de datos | PostgreSQL, SQLAlchemy ORM         |
| Frontend      | HTML5, CSS3, Bootstrap 5, Chart.js |
| Reportes      | Pandas, OpenPyXL (Excel), ReportLab (PDF) |
| Seguridad     | bcrypt (hash de contraseñas)       |

---

## ⚙️ Requisitos previos (en el servidor)

- **Python 3.10 o superior** instalado.
- **PostgreSQL** instalado y en ejecución.
- **Conexión de red local**: el servidor debe tener una IP fija accesible para los clientes.
- **Opcional**: `git` para clonar el repositorio.

---

## 🚀 Instalación y despliegue

### 1. Clonar el repositorio (o copiar los archivos)

```bash
git clone https://github.com/tuusuario/VicarWeb.git
cd VicarWeb
