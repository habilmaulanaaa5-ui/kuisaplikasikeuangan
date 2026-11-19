import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import date

st.set_page_config(
    page_title="MoneyMate",
    page_icon="💰",
    layout="wide"
)

# ==================================
# CLASS TRANSAKSI (KONSEP PBO)
# ==================================

class Transaksi:
    def __init__(self, tanggal, jenis, kategori, nominal, keterangan):
        self.tanggal = tanggal
        self.jenis = jenis
        self.kategori = kategori
        self.nominal = float(nominal)
        self.keterangan = keterangan

    def tambah(self):
        return {
            "Tanggal": str(self.tanggal),
            "Jenis": self.jenis,
            "Kategori": self.kategori,
            "Nominal": self.nominal,
            "Keterangan": self.keterangan
        }

    def ubah(self, tanggal, jenis, kategori, nominal, keterangan):
        self.tanggal = tanggal
        self.jenis = jenis
        self.kategori = kategori
        self.nominal = float(nominal)
        self.keterangan = keterangan

    def hapus(self):
        return True


# ==================================
# SESSION STATE
# ==================================

if "daftar_transaksi" not in st.session_state:
    st.session_state.daftar_transaksi = []

if "form_edit" not in st.session_state:
    st.session_state.form_edit = None


# ==================================
# FUNGSI BANTU
# ==================================

def rupiah(angka):
    return f"Rp{angka:,.0f}".replace(",", ".")


def hitung_keuangan():
    pemasukan = sum(
        t.nominal for t in st.session_state.daftar_transaksi
        if t.jenis == "Pemasukan"
    )

    pengeluaran = sum(
        t.nominal for t in st.session_state.daftar_transaksi
        if t.jenis == "Pengeluaran"
    )

    saldo = pemasukan - pengeluaran

    return pemasukan, pengeluaran, saldo


def buat_dataframe():
    data = [
        t.tambah()
        for t in st.session_state.daftar_transaksi
    ]

    return pd.DataFrame(data)


# ==================================
# HEADER DAN NAVIGASI
# ==================================

st.title("💰 MoneyMate")
st.caption("Aplikasi Pengelola Keuangan Mahasiswa")

st.write(
    "Catat pemasukan dan pengeluaranmu "
    "agar keuangan lebih teratur."
)

with st.sidebar:
    st.title("💰 MoneyMate")

    menu = option_menu(
        menu_title="Menu Utama",
        options=[
            "Dashboard",
            "Transaksi",
            "Laporan Keuangan"
        ],
        icons=[
            "house-door",
            "wallet2",
            "bar-chart-line"
        ],
        default_index=0
    )


# ==================================
# MENU 1: DASHBOARD
# ==================================

if menu == "Dashboard":

    st.header("📊 Dashboard Keuangan")

    pemasukan, pengeluaran, saldo = hitung_keuangan()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Pemasukan",
        rupiah(pemasukan)
    )

    col2.metric(
        "Total Pengeluaran",
        rupiah(pengeluaran)
    )

    col3.metric(
        "Saldo Saat Ini",
        rupiah(saldo)
    )

    st.divider()

    st.subheader("Transaksi Terbaru")

    if st.session_state.daftar_transaksi:

        df = buat_dataframe()

        st.dataframe(
            df.sort_values(
                "Tanggal",
                ascending=False
            ).head(5),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Belum ada transaksi.")

    st.subheader("Grafik Pengeluaran")

    if pengeluaran > 0:

        data_pengeluaran = [
            {
                "Kategori": t.kategori,
                "Nominal": t.nominal
            }
            for t in st.session_state.daftar_transaksi
            if t.jenis == "Pengeluaran"
        ]

        df_grafik = pd.DataFrame(data_pengeluaran)

        ringkasan = df_grafik.groupby(
            "Kategori"
        )["Nominal"].sum()

        st.bar_chart(ringkasan)

    else:
        st.info("Belum ada data pengeluaran.")


# ==================================
# MENU 2: TRANSAKSI
# ==================================

elif menu == "Transaksi":

    st.header("💳 Kelola Transaksi")

    tab1, tab2 = st.tabs([
        "➕ Tambah Transaksi",
        "📋 Daftar Transaksi"
    ])

    # TAMBAH TRANSAKSI

    with tab1:

        st.subheader("Tambah Transaksi Baru")

        with st.form("form_tambah", clear_on_submit=True):

            tanggal = st.date_input(
                "Tanggal",
                value=date.today()
            )

            jenis = st.selectbox(
                "Jenis Transaksi",
                ["Pemasukan", "Pengeluaran"]
            )

            if jenis == "Pemasukan":

                kategori_list = [
                    "Uang Saku",
                    "Beasiswa",
                    "Gaji Part Time",
                    "Hadiah",
                    "Lainnya"
                ]

            else:

                kategori_list = [
                    "Makanan",
                    "Transportasi",
                    "Kebutuhan Kuliah",
                    "Pulsa/Internet",
                    "Hiburan",
                    "Belanja",
                    "Lainnya"
                ]

            kategori = st.selectbox(
                "Kategori",
                kategori_list
            )

            nominal = st.number_input(
                "Nominal (Rp)",
                min_value=0,
                step=1000
            )

            keterangan = st.text_input(
                "Keterangan",
                placeholder="Contoh: Uang makan mingguan"
            )

            simpan = st.form_submit_button(
                "Simpan Transaksi",
                use_container_width=True
            )

            if simpan:

                if nominal <= 0:

                    st.error(
                        "Nominal harus lebih dari Rp0."
                    )

                else:

                    transaksi_baru = Transaksi(
                        tanggal,
                        jenis,
                        kategori,
                        nominal,
                        keterangan
                    )

                    st.session_state.daftar_transaksi.append(
                        transaksi_baru
                    )

                    st.success(
                        "Transaksi berhasil ditambahkan!"
                    )

                    st.rerun()

    # TAMPILKAN TRANSAKSI

    with tab2:

        st.subheader("Daftar Semua Transaksi")

        if st.session_state.daftar_transaksi:

            for i, transaksi in enumerate(
                st.session_state.daftar_transaksi
            ):

                tanda = (
                    "+"
                    if transaksi.jenis == "Pemasukan"
                    else "-"
                )

                with st.expander(
                    f"{i + 1}. {transaksi.kategori} | "
                    f"{tanda}{rupiah(transaksi.nominal)}"
                ):

                    st.write(
                        f"**Tanggal:** {transaksi.tanggal}"
                    )

                    st.write(
                        f"**Jenis:** {transaksi.jenis}"
                    )

                    st.write(
                        f"**Keterangan:** "
                        f"{transaksi.keterangan or '-'}"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button(
                            "✏️ Edit",
                            key=f"edit_{i}"
                        ):

                            st.session_state.form_edit = i
                            st.rerun()

                    with col2:

                        if st.button(
                            "🗑️ Hapus",
                            key=f"hapus_{i}"
                        ):

                            transaksi.hapus()

                            st.session_state.daftar_transaksi.pop(i)

                            st.session_state.form_edit = None

                            st.success(
                                "Transaksi berhasil dihapus."
                            )

                            st.rerun()

            # FORM EDIT TRANSAKSI

            if st.session_state.form_edit is not None:

                indeks = st.session_state.form_edit

                if 0 <= indeks < len(
                    st.session_state.daftar_transaksi
                ):

                    data_edit = (
                        st.session_state.daftar_transaksi[indeks]
                    )

                    st.divider()

                    st.subheader("✏️ Ubah Transaksi")

                    with st.form("form_edit_data"):

                        tanggal_baru = st.date_input(
                            "Tanggal",
                            value=pd.to_datetime(
                                data_edit.tanggal
                            ).date()
                        )

                        jenis_baru = st.selectbox(
                            "Jenis",
                            ["Pemasukan", "Pengeluaran"],
                            index=[
                                "Pemasukan",
                                "Pengeluaran"
                            ].index(data_edit.jenis)
                        )

                        if jenis_baru == "Pemasukan":

                            kategori_list_baru = [
                                "Uang Saku",
                                "Beasiswa",
                                "Gaji Part Time",
                                "Hadiah",
                                "Lainnya"
                            ]

                        else:

                            kategori_list_baru = [
                                "Makanan",
                                "Transportasi",
                                "Kebutuhan Kuliah",
                                "Pulsa/Internet",
                                "Hiburan",
                                "Belanja",
                                "Lainnya"
                            ]

                        index_kategori = (
                            kategori_list_baru.index(
                                data_edit.kategori
                            )
                            if data_edit.kategori in kategori_list_baru
                            else 0
                        )

                        kategori_baru = st.selectbox(
                            "Kategori",
                            kategori_list_baru,
                            index=index_kategori
                        )

                        nominal_baru = st.number_input(
                            "Nominal (Rp)",
                            min_value=0,
                            value=int(data_edit.nominal),
                            step=1000
                        )

                        keterangan_baru = st.text_input(
                            "Keterangan",
                            value=data_edit.keterangan
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            ubah = st.form_submit_button(
                                "Simpan Perubahan",
                                use_container_width=True
                            )

                        with col2:

                            batal = st.form_submit_button(
                                "Batal",
                                use_container_width=True
                            )

                        if ubah:

                            if nominal_baru <= 0:

                                st.error(
                                    "Nominal harus lebih dari Rp0."
                                )

                            else:

                                data_edit.ubah(
                                    tanggal_baru,
                                    jenis_baru,
                                    kategori_baru,
                                    nominal_baru,
                                    keterangan_baru
                                )

                                st.session_state.form_edit = None

                                st.success(
                                    "Transaksi berhasil diperbarui."
                                )

                                st.rerun()

                        if batal:

                            st.session_state.form_edit = None

                            st.rerun()

        else:

            st.info("Belum ada data transaksi.")


# ==================================
# MENU 3: LAPORAN KEUANGAN
# ==================================

elif menu == "Laporan Keuangan":

    st.header("📈 Laporan Keuangan")

    pemasukan, pengeluaran, saldo = hitung_keuangan()

    st.subheader("Ringkasan Keuangan")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Pemasukan",
        rupiah(pemasukan)
    )

    col2.metric(
        "Pengeluaran",
        rupiah(pengeluaran)
    )

    col3.metric(
        "Saldo Akhir",
        rupiah(saldo)
    )

    st.divider()

    st.subheader("Riwayat Transaksi")

    if st.session_state.daftar_transaksi:

        df = buat_dataframe()

        df["Nominal"] = df["Nominal"].apply(rupiah)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        # DOWNLOAD LAPORAN

        st.download_button(
            "⬇️ Download Laporan CSV",
            data=buat_dataframe().to_csv(
                index=False
            ).encode("utf-8"),
            file_name="laporan_keuangan_mahasiswa.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "Belum ada transaksi untuk ditampilkan."
        )

    st.divider()

    st.subheader("Kesimpulan Keuangan")

    if saldo > 0:

        st.success(
            "Keuangan kamu masih memiliki saldo positif. "
            "Tetap atur pengeluaran dengan baik!"
        )

    elif saldo < 0:

        st.warning(
            "Pengeluaran lebih besar daripada pemasukan. "
            "Coba kurangi pengeluaran."
        )

    else:

        st.info(
            "Saldo kamu saat ini Rp0 atau belum ada transaksi."
        )


# ==================================
# FOOTER
# ==================================

st.divider()
