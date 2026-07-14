# -*- coding: utf-8 -*-
"""
app.py
Entry point SIPAKAR AHP DDTC Library (Sistem Prioritas Koleksi Perpustakaan
berbasis AHP). Menangani inisialisasi database, login, dan routing halaman.

Jalankan dengan:
    streamlit run app.py
"""
import streamlit as st

from db.database import db_exists, init_schema
from db.seed import run_seed
from core import auth

st.set_page_config(
    page_title="SIPAKAR AHP - DDTC Library",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Inisialisasi database & seed data pada run pertama ---
if not db_exists():
    init_schema()
    with st.spinner("Menyiapkan database & memuat data awal (100 buku, 8 kriteria, rubrik)..."):
        run_seed()

if "user" not in st.session_state:
    st.session_state["user"] = None


def render_login():
    st.markdown(
        """
        <div style="text-align:center; padding-top: 40px;">
            <h1 style="color:#0B2F64; margin-bottom:0;">📚 SIPAKAR AHP</h1>
            <p style="color:#64748B; font-size:16px;">Sistem Prioritas Koleksi Perpustakaan berbasis AHP<br>
            Danny Darussalam Tax Center (DDTC) Library</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        with st.form("login_form"):
            st.markdown("#### 🔐 Login Internal")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Masuk", use_container_width=True, type="primary")
            if submitted:
                if auth.do_login(username, password):
                    st.success("Login berhasil!")
                    st.rerun()
                else:
                    st.error("Username atau password salah, atau akun tidak aktif.")
        st.caption(
            "Akses sistem ini terbatas untuk pengguna internal (Admin & Pustakawan) DDTC Library. "
            "Akun default awal: **admin** / **pustakawan** (password lihat db/seed.py — segera ganti setelah login pertama)."
        )


def render_sidebar_user_box():
    auth.sidebar_user_box()


if not auth.is_logged_in():
    render_login()
else:
    render_sidebar_user_box()
    st.markdown("## 📚 SIPAKAR AHP — DDTC Library")
    st.markdown(
        "Sistem Pendukung Keputusan penentuan **prioritas pengembangan koleksi buku pajak** "
        "menggunakan metode **Analytical Hierarchy Process (AHP)** multi-pakar berbasis rubrik data objektif."
    )
    st.info("👈 Pilih halaman pada menu sebelah kiri untuk mulai bekerja: Dashboard, Data Buku, "
            "Kriteria & Rubrik, Data Pakar, Perbandingan Kriteria, Proses & Hasil AHP, Analisis Anggaran, "
            "Laporan, Riwayat Perhitungan, dan Manajemen Pengguna.")

    from db import repository as repo
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Total Buku Usulan", repo.count_buku())
    c2.metric("🧑‍🏫 Pakar Aktif", repo.count_pakar())
    c3.metric("🧭 Kriteria", len(repo.list_kriteria()))
    latest = repo.get_latest_batch()
    c4.metric("🧮 Batch Terakhir", latest["batch_id"] if latest else "Belum ada")
