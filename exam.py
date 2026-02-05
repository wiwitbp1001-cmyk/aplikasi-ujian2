import streamlit as st
import pandas as pd
import random
import time

# --- CONFIG ---
def init_session():
    if 'exam_started' not in st.session_state:
        st.session_state.exam_started = False
    if 'current_idx' not in st.session_state:
        st.session_state.current_idx = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0

def main():
    st.set_page_config(page_title="Secure Exam Pro", layout="centered")
    init_session()

    # 1. SETUP & UPLOAD
    if not st.session_state.exam_started:
        st.title("🛡️ Secure Exam Setup")
        st.info("Silakan unggah file Excel soal dan masukkan data diri.")
        
        uploaded_file = st.file_uploader("Upload Template Soal (XLSX)", type=['xlsx'])
        nama = st.text_input("Nama Lengkap Peserta")
        nisn = st.text_input("NISN / ID Peserta", type="password")
        durasi = st.number_input("Durasi Ujian (Menit)", min_value=1, value=10)

        if st.button("🚀 Mulai Ujian Sekarang") and uploaded_file and nama:
            df = pd.read_excel(uploaded_file)
            questions = []
            for _, row in df.iterrows():
                questions.append({
                    "q": row['Soal'],
                    "opt": [row['A'], row['B'], row['C'], row['D'], row['E']],
                    "a": row['Jawaban']
                })
            
            random.shuffle(questions)
            st.session_state.questions = questions
            st.session_state.nama = nama
            st.session_state.start_time = time.time()
            st.session_state.limit = durasi * 60
            st.session_state.exam_started = True
            st.rerun()

    # 2. HALAMAN UJIAN
    else:
        # Hitung Waktu
        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.limit - elapsed)

        if remaining <= 0 or st.session_state.current_idx >= len(st.session_state.questions):
            show_result()
        else:
            # UI Ujian
            st.sidebar.metric("⏳ Sisa Waktu", f"{remaining // 60}m {remaining % 60}s")
            st.sidebar.write(f"👤 Peserta: {st.session_state.nama}")
            
            curr_q = st.session_state.questions[st.session_state.current_idx]
            
            st.subheader(f"Soal {st.session_state.current_idx + 1}")
            st.write(curr_q["q"])
            
            # Acak opsi agar tidak bisa contek urutan
            options = curr_q["opt"]
            
            ans = st.radio("Pilih jawaban:", options, key=f"ans_{st.session_state.current_idx}")
            
            if st.button("Konfirmasi & Lanjut"):
                if ans == curr_q["a"]:
                    st.session_state.score += 1
                st.session_state.current_idx += 1
                st.rerun()

def show_result():
    st.title("🏁 Ujian Selesai")
    st.balloons()
    score_final = (st.session_state.score / len(st.session_state.questions)) * 100
    st.metric("Skor Anda", f"{score_final:.2f}")
    st.write(f"Terima kasih {st.session_state.nama}, jawaban Anda telah tersimpan di sistem.")
    if st.button("Keluar"):
        st.session_state.clear()
        st.rerun()

if __name__ == "__main__":
    main()
