
import streamlit as st
import urllib.parse
st.set_page_config(
    page_title="Tienda de Gallinas",
    page_icon="🐔",
    layout="wide"
)

st.title("🐔 Tienda de Gallinas")
st.subheader("Gallinas saludables para tu granja")

st.write("Bienvenido a nuestra tienda online.")

st.divider()

supabase_url = st.secrets["SUPABASE_URL"]
supabase_key = st.secrets["SUPABASE_KEY"]

from supabase import create_client
supabase = create_client(supabase_url, supabase_key)

st.header("Nuestros productos")

try:
    resultado = supabase.table("productos").select("*").execute()
    productos = resultado.data

    if not productos:
        st.info("Todavía no hay productos registrados.")
    else:
        columnas = st.columns(3)

        for i, producto in enumerate(productos):
            with columnas[i % 3]:
                st.subheader(f"🐔 {producto['nombre']}")
                st.write(producto.get("descripcion") or "")
                st.write(f"Precio: Bs {producto['precio']}")
                st.write(f"Cantidad disponible: {producto['cantidad']}")

                mensaje = f"Hola, quiero consultar por {producto['nombre']}. ¿Está disponible?"
                url_whatsapp = "https://wa.me/59160468689?text=" + urllib.parse.quote(mensaje)
                st.link_button("Consultar por WhatsApp", url_whatsapp)
                st.write(f"Cantidad disponible: {producto['cantidad']}")

except Exception as e:
    st.error(f"No se pudieron cargar los productos: {e}")

st.divider()

st.subheader("📞 Contacto")
st.write("Pronto podrás realizar tus pedidos por WhatsApp.")

st.sidebar.header("Estado de la conexión")

try:
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
    st.sidebar.success("Configuración de Supabase encontrada")


except Exception as e:
    st.sidebar.error(f"Error de Supabase: {e}")

try:
    from supabase import create_client

    supabase = create_client(supabase_url, supabase_key)
    resultado = supabase.table("productos").select("*").limit(5).execute()

    st.sidebar.success("¡Conexión con Supabase funcionando!")
    st.sidebar.write("Productos encontrados:", len(resultado.data))

except Exception as e:
    st.sidebar.error(f"Error de conexión: {e}")


try:
    from supabase import create_client

    supabase = create_client(supabase_url, supabase_key)
    resultado = supabase.table("productos").select("*").limit(5).execute()

    st.sidebar.success("¡Conexión con Supabase funcionando!")
    st.sidebar.write("Productos encontrados:", len(resultado.data))

except Exception as e:
    st.sidebar.error(f"Error de conexión: {e}")
