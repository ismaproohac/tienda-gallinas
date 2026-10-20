import urllib.parse
import uuid
import streamlit as st
from supabase import create_client


# --------------------------------------------------
# Configuración y conexión con Supabase
# --------------------------------------------------
st.set_page_config(
    page_title="Tienda de Gallinas",
    page_icon="🐔",
    layout="wide",
)

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

# Conexión pública: leer productos y registrar Me gusta
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# --------------------------------------------------
# Estado de sesión del administrador
# --------------------------------------------------
if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False


# --------------------------------------------------
# Encabezado
# --------------------------------------------------
st.title("🐔 Tienda de Gallinas")
st.subheader("Gallinas saludables para tu granja")
st.write("Bienvenido a nuestra tienda online.")
st.header("Nuestros productos")
try:
   
    resultado = supabase.table("productos").select("*").execute()
    productos = resultado.data or []

    categorias_disponibles = sorted({
        (producto.get("categoria") or "").strip()
        for producto in productos
        if (producto.get("categoria") or "").strip()
    })

    opciones_categoria = ["Todas"] + categorias_disponibles

    categoria_seleccionada = st.selectbox(
        "📂 Filtrar por categoría",
        opciones_categoria,
        key="filtro_categoria_tienda",
    
    )

    busqueda = st.text_input(
        "🔎 Buscar producto",
        placeholder="Escribe el nombre del producto..."
    )

    # Filtrar por categoría
    if categoria_seleccionada != "Todas":
        productos = [
            producto
            for producto in productos
            if (producto.get("categoria") or "").strip()
             == categoria_seleccionada
        ]

    # Filtrar por búsqueda
    if busqueda:
        productos = [
            producto
            for producto in productos
            if busqueda.lower() in producto.get("nombre", "").lower()
            or busqueda.lower()
            in producto.get("descripcion", "").lower()
        ]

    # Mostrar productos una sola vez
    if not productos:
        st.info("No se encontraron productos.")
    else:
        columnas = st.columns(3)

        for i, producto in enumerate(productos):
            with columnas[i % 3]:
                with st.container(border=True):

                    if producto.get("imagen_url"):
                        st.markdown(
                            f"""
                            <div style="
                                width: 100%;
                                height: 180px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                background-color: #f7f7f7;
                                border-radius: 8px;
                                overflow: hidden;
                            ">
                                <img
                                    src="{producto['imagen_url']}"
                                    alt="Foto del producto"
                                    style="
                                        width: 100%;
                                        height: 180px;
                                        object-fit: contain;
                                    "
                                />
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                        
                        

                    st.subheader(f"🐔 {producto['nombre']}")

                    st.write(producto.get("descripcion", ""))

                    cantidad_disponible = int(
                        producto.get("cantidad") or 0
                    )

                    if cantidad_disponible > 0:
                        st.write(
                            f"💰 Precio: Bs {producto.get('precio', 0)}"
                        )
                        st.write(
                            f"📦 Cantidad disponible: {cantidad_disponible}"
                        )
                    else:
                        st.info(
                            "⏳ Próximamente: aún no disponible para la venta."
                        )

                    st.write(
                        f"👍 Me gusta: {producto.get('me_gusta', 0)}"
                    )

                    if st.button(
                        "👍 Me gusta",
                        key=f"like_{producto['id']}_{i}"
                    ):
                        supabase.rpc(
                            "incrementar_me_gusta",
                            {"p_producto_id": producto["id"]}
                        ).execute()

                        st.rerun()

                    enlace_tienda = (
                        "https://ismaproohac-tienda-gallinas-app-u5a7cb.streamlit.app/"
                    )

                    nombre_producto = producto["nombre"]
                    precio_producto = producto["precio"]

                    mensaje = (
                        f"Hola, quiero consultar por {nombre_producto}, "
                        f"con precio de Bs {precio_producto}. "
                        "¿Está disponible?"
                    )

                    url = (
                        "https://wa.me/59160468689?text="
                        + urllib.parse.quote(mensaje)
                    )

                    st.link_button(
                        "🟢 Consultar por WhatsApp",
                        url
                    )

                    mensaje_facebook = (
                        f"🐔 ¡Mira este producto de nuestra Tienda de Gallinas! "
                        f"{nombre_producto} por Bs {precio_producto}. "
                        f"Consulta aquí: {enlace_tienda}"
                    )

                    enlace_facebook = (
                        "https://www.facebook.com/sharer/sharer.php?u="
                        + urllib.parse.quote(enlace_tienda)
                        + "&quote="
                        + urllib.parse.quote(mensaje_facebook)
                    )

                    st.link_button(
                        "🔵 Compartir en Facebook",
                        enlace_facebook
                    )

                    st.caption("📋 Copia este texto para tu publicación:")
                    st.code(mensaje_facebook, language=None)

except Exception as e:
    st.error(f"Error al cargar los productos: {e}")

# --------------------------------------------------
# Panel privado de administración
# --------------------------------------------------
with st.sidebar:
    st.subheader("🔐 Administración")

    if not st.session_state.admin_autenticado:
        clave = st.text_input(
            "Contraseña de administrador",
            type="password",
            key="clave_admin",
        )

        if st.button("Iniciar sesión"):
            try:
                if clave == st.secrets["admin"]["password"]:
                    st.session_state.admin_autenticado = True
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta")
            except Exception:
                st.error(
                    "No se encontró la contraseña de administrador "
                    "en los secretos de la aplicación."
                )

    else:
        st.success("Sesión de administrador iniciada")
        with st.expander("✏️ Editar producto", expanded=False):
            try:
                supabase_admin = create_client(
                    SUPABASE_URL,
                    st.secrets["SUPABASE_ADMIN_KEY"],
                )

                respuesta = (
                    supabase_admin.table("productos")
                    .select("*")
                    .execute()
                )
                productos_editar = respuesta.data or []

            except Exception as e:
                st.error(f"No se pudieron cargar los productos: {e}")
                productos_editar = []

            if productos_editar:
                opciones = {
                    f"{p['nombre']} (ID {p['id']})": p
                    for p in productos_editar
                }

                seleccionado = st.selectbox(
                    "Selecciona el producto",
                    list(opciones.keys()),
                    key="producto_a_editar",
                )
                producto_actual = opciones[seleccionado]

                with st.form("form_editar_producto"):
                    nombre_editado = st.text_input(
                        "Nombre",
                        value=str(producto_actual.get("nombre") or ""),
                    )

                    descripcion_editada = st.text_area(
                        "Descripción",
                        value=str(producto_actual.get("descripcion") or ""),
                    )

                    precio_editado = st.number_input(
                        "Precio (Bs)",
                        min_value=0.0,
                        value=float(producto_actual.get("precio") or 0),
                        step=1.0,
                    )

                    cantidad_editada = st.number_input(
                        "Cantidad disponible",
                        min_value=0,
                        value=int(producto_actual.get("cantidad") or 0),
                        step=1,
                    )

                    imagen_editada = st.file_uploader(
                        "Cambiar foto (opcional)",
                        type=["jpg", "jpeg", "png", "webp"],
                         key=f"imagen_editar_producto_{producto_actual['id']}",
                    )

                    guardar_cambios = st.form_submit_button(
                        "Guardar cambios"
                    )

                if guardar_cambios:
                    if not nombre_editado.strip():
                        st.error("Escribe el nombre del producto.")
                    else:
                        try:
                            cambios = {
                                "nombre": nombre_editado.strip(),
                                "descripcion": descripcion_editada.strip(),
                                "precio": precio_editado,
                                "cantidad": cantidad_editada,
                            }

                            if imagen_editada is not None:
                                extension = (
                                    imagen_editada.name.rsplit(".", 1)[-1]
                                    .lower()
                                )
                                ruta_imagen = (
                                    f"productos/{uuid.uuid4().hex}.{extension}"
                                )

                                supabase_admin.storage.from_(
                                    "fotos-productos"
                                ).upload(
                                    path=ruta_imagen,
                                    file=imagen_editada.getvalue(),
                                    file_options={
                                        "content-type": imagen_editada.type,
                                        "upsert": "false",
                                    },
                                )

                                cambios["imagen_url"] = (
                                    supabase_admin.storage.from_(
                                        "fotos-productos"
                                    ).get_public_url(ruta_imagen)
                                )

                            (
                                supabase_admin.table("productos")
                                .update(cambios)
                                .eq("id", producto_actual["id"])
                                .execute()
                            )

                            st.success("¡Producto actualizado correctamente!")
                            st.rerun()

                        except Exception as e:
                            st.error("No se pudo actualizar el producto:")
                            st.code(str(e))
            else:
                st.info("Todavía no hay productos para editar.")

        with st.expander("🗑️ Eliminar producto", expanded=False):
            productos_eliminar = []

            try:
                
                supabase_admin_eliminar = create_client(
                    SUPABASE_URL,
                    st.secrets["SUPABASE_ADMIN_KEY"],
                )

                respuesta_eliminar = (
                    supabase_admin_eliminar.table("productos")
                    .select("id, nombre, imagen_url")
                    .execute()
                )
                productos_eliminar = respuesta_eliminar.data or []

                producto
                _eliminar = respuesta_eliminar.data or []

            except Exception as e:
                st.error(f"No se pudieron cargar los productos: {e}")

            if productos_eliminar:
                opciones_eliminar = {
                    f"{p['nombre']} (ID {p['id']})": p
                    for p in productos_eliminar
                }

                seleccionado_eliminar = st.selectbox(
                    "Selecciona el producto que deseas eliminar",
                    list(opciones_eliminar.keys()),
                    key="producto_a_eliminar",
                )

                producto_eliminar = opciones_eliminar[
                    seleccionado_eliminar
                ]

                confirmar_eliminar = st.checkbox(
                    f"Confirmo que quiero eliminar "
                    f"{producto_eliminar['nombre']}",
                    key="confirmar_eliminar_producto",
                )

                if st.button(
                    "🗑️ Eliminar definitivamente",
                    key="boton_eliminar_producto",
                ):
                    if not confirmar_eliminar:
                        st.warning(
                            "Marca la casilla de confirmación antes de eliminar."
                        )
                    else:
                        try:
                            (
                                supabase_admin_eliminar.table("productos")
                                .delete()
                                .eq("id", producto_eliminar["id"])
                                .execute()
                            )

                            st.success("¡Producto eliminado correctamente!")
                            st.rerun()

                        except Exception as e:
                            st.error("No se pudo eliminar el producto:")
                            st.code(str(e))

            else:
                st.info("No hay productos para eliminar.")
        if st.button("🔒 Cerrar sesión", key="cerrar_sesion_admin"):
            st.session_state.admin_autenticado = False
            st.rerun()
        st.subheader("➕ Agregar producto")

        with st.form("form_agregar_producto", clear_on_submit=True):
            nombre = st.text_input("Nombre del producto")
            descripcion = st.text_area("Descripción")
            categoria = st.selectbox(
    "Categoría del producto",
    [
        "Gallinas ponedoras",
        "Gallinas criollas",
        "Pollitos",
        "Otros",
    ],
    key="categoria_nuevo_producto",
)

            imagen = st.file_uploader(
    "📷 Foto del producto",
    type=["jpg", "jpeg", "png", "webp"],
    key="imagen_nuevo_producto",

)
            precio = st.number_input(
                "Precio (Bs)", min_value=0.0, step=1.0
            )
            cantidad = st.number_input(
                "Cantidad disponible", min_value=0, step=1
            )
            guardar = st.form_submit_button("Guardar producto")

        if guardar:
            if not nombre.strip():
                st.error("Escribe el nombre del producto.")
            elif "SUPABASE_ADMIN_KEY" not in st.secrets:
                st.error(
                    "Falta configurar SUPABASE_ADMIN_KEY en los secretos. "
                    "No se ha guardado el producto."
                )
            else:
               
                try:
                    supabase_admin = create_client(
                        SUPABASE_URL,
                        st.secrets["SUPABASE_ADMIN_KEY"],
                    )
                    imagen_url = None

                    if imagen is not None:
                        extension = imagen.name.rsplit(".", 1)[-1].lower()
                        ruta_imagen = (
                            f"productos/{uuid.uuid4().hex}.{extension}"
                        )

                        supabase_admin.storage.from_(
                            "fotos-productos"
                        ).upload(
                            path=ruta_imagen,
                            file=imagen.getvalue(),
                            file_options={
                                "content-type": imagen.type,
                                "upsert": "false",
                            },
                        )

                        imagen_url = supabase_admin.storage.from_(
                            "fotos-productos"
                        ).get_public_url(ruta_imagen)

                    nuevo_producto = {
                        "nombre": nombre.strip(),
                        "descripcion": descripcion.strip(),
                        "precio": precio,
                        "cantidad": cantidad,
                        "categoria": categoria,
                        "me_gusta": 0,
                        "imagen_url": imagen_url,
                       }

                    supabase_admin.table("productos").insert(
                        nuevo_producto
                    ).execute()

                    st.success("¡Producto agregado correctamente!")
                    st.rerun()

                except Exception as e:
                    st.error("Error real al guardar el producto:")
                    st.code(str(e))

if st.button("Cerrar sesión"):
            st.session_state.admin_autenticado = False
            st.rerun()


# --------------------------------------------------
# Catálogo público
# --------------------------------------------------
st.header("Nuestros productos")

try:
    resultado = (
        supabase.table("productos")
        .select("*")
        .order("id")
        .execute()
    )
    productos = resultado.data or []

    if not productos:
        st.info("Todavía no hay productos registrados.")
    else:
        columnas = st.columns(3)

        for i, producto in enumerate(productos):
            with columnas[i % 3]:

                if producto.get("imagen_url"):
                    st.markdown(
                        f"""
                        <div style="
                            width: 100%;
                            height: 180px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            background-color: #f7f7f7;
                            border-radius: 8px;
                            overflow: hidden;
                        ">
                            <img
                                src="{producto['imagen_url']}"
                                alt="Foto del producto"
                                style="
                                    max-width: 100%;
                                    max-height: 170px;
                                    width: auto;
                                    height: auto;
                                    object-fit: contain;
                                "
                            />
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
    

                mensaje = (
                    f"Hola, quiero consultar por {producto['nombre']}. "
                    "¿Está disponible?"
                )
                url_whatsapp = (
                    "https://wa.me/59160468689?text="
                    + urllib.parse.quote(mensaje)
                )
                st.link_button("Consultar por WhatsApp", url_whatsapp)

except Exception as e:
    st.error(f"No se pudieron cargar los productos: {e}")


# --------------------------------------------------
# Contacto y estado de conexión
# --------------------------------------------------
st.divider()
st.subheader("📞 Contacto")
st.write("Pronto podrás realizar tus pedidos por WhatsApp.")

with st.sidebar:
    st.divider()
    st.header("Estado de la conexión")
    try:
        prueba = (
            supabase.table("productos")
            .select("id")
            .limit(1)
            .execute()
        )
        st.success("Conexión con Supabase funcionando")
    except Exception as e:
        st.error("No se pudo conectar con Supabase.")
        st.caption(f"Detalle técnico: {e}")
