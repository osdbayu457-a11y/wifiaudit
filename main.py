"""WiFi Audit — versi Kivy (APK)."""
import os
import sys
import threading
from pathlib import Path

# Setup path supaya core/ bisa diimpor
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp

from core.dictionary import load_common, load_router_defaults, guess_brand
from core.strength import analyze

Window.clearcolor = (0.05, 0.07, 0.1, 1)


class MenuUtama(BoxLayout):
    def __init__(self, **kw):
        super().__init__(orientation="vertical", padding=dp(16), spacing=dp(10), **kw)

        self.kamus_umum = load_common()
        self.kamus_router = load_router_defaults()

        # Header
        judul = Label(
            text="[b]WiFi Audit[/b]\nAudit Kekuatan Password WiFi",
            markup=True, font_size=dp(22), size_hint_y=None, height=dp(70),
            halign="center", valign="middle"
        )
        judul.bind(size=judul.setter('text_size'))
        self.add_widget(judul)

        # Info kamus
        info = Label(
            text=f"Kamus: {len(self.kamus_umum)} password, {len(self.kamus_router)} merek router",
            font_size=dp(12), color=(0.6, 0.6, 0.6, 1),
            size_hint_y=None, height=dp(25)
        )
        self.add_widget(info)

        # Peringatan
        peringatan = Label(
            text="[color=ffcc00]Hanya untuk jaringan milik sendiri.\n"
                 "Penggunaan pada jaringan orang lain melanggar UU ITE.[/color]",
            markup=True, font_size=dp(12),
            size_hint_y=None, height=dp(50),
            halign="center"
        )
        peringatan.bind(size=peringatan.setter('text_size'))
        self.add_widget(peringatan)

        # Tombol menu
        for teks, aksi in [
            ("Analisis Password Manual", self.buka_analisis),
            ("Pindai WiFi Sekitar", self.buka_scan),
            ("Info Aplikasi", self.buka_info),
            ("Keluar", self.keluar),
        ]:
            btn = Button(
                text=teks, font_size=dp(16),
                size_hint_y=None, height=dp(55),
                background_color=(0.15, 0.35, 0.6, 1)
            )
            btn.bind(on_press=aksi)
            self.add_widget(btn)

    def buka_analisis(self, *args):
        popup = PopupAnalisis(self.kamus_umum, self.kamus_router)
        popup.open()

    def buka_scan(self, *args):
        popup = PopupPesan(
            "Pindai WiFi",
            "Fitur pindai WiFi membutuhkan Shizuku + rish.\n\n"
            "Di versi APK ini, fitur tersebut belum disertakan "
            "karena butuh setup Shizuku terpisah.\n\n"
            "Gunakan versi Termux untuk pindai WiFi."
        )
        popup.open()

    def buka_info(self, *args):
        popup = PopupPesan(
            "Tentang WiFi Audit",
            "WiFi Audit v1.0\n\n"
            "Alat analisis kekuatan password WiFi.\n"
            "Menggunakan kamus password umum (97.746 kata) "
            "dan default router Indonesia.\n\n"
            "Dibangun dengan Python + Kivy.\n"
            "Sumber: github.com/osdbayu457-a11y/wifiaudit"
        )
        popup.open()

    def keluar(self, *args):
        App.get_running_app().stop()


class PopupAnalisis(Popup):
    def __init__(self, kamus_umum, kamus_router, **kw):
        super().__init__(**kw)
        self.title = "Analisis Password"
        self.size_hint = (0.9, 0.8)
        self.kamus_umum = kamus_umum
        self.kamus_router = kamus_router

        layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))

        layout.add_widget(Label(
            text="Masukkan password yang mau dianalisis:",
            size_hint_y=None, height=dp(30)
        ))

        self.input_pw = TextInput(
            password=True, multiline=False,
            size_hint_y=None, height=dp(45),
            font_size=dp(16)
        )
        layout.add_widget(self.input_pw)

        layout.add_widget(Label(
            text="Nama SSID (opsional, untuk tebak merek):",
            size_hint_y=None, height=dp(30)
        ))

        self.input_ssid = TextInput(
            multiline=False, size_hint_y=None, height=dp(45),
            font_size=dp(16)
        )
        layout.add_widget(self.input_ssid)

        btn_analisis = Button(
            text="Analisis", size_hint_y=None, height=dp(50),
            background_color=(0.15, 0.5, 0.3, 1)
        )
        btn_analisis.bind(on_press=self.jalankan_analisis)
        layout.add_widget(btn_analisis)

        # Area hasil
        scroll = ScrollView()
        self.hasil = Label(
            text="", markup=True, font_size=dp(14),
            size_hint_y=None, halign="left", valign="top"
        )
        self.hasil.bind(
            width=lambda *x: setattr(self.hasil, 'text_size', (self.hasil.width, None)),
            texture_size=lambda *x: setattr(self.hasil, 'height', self.hasil.texture_size[1])
        )
        scroll.add_widget(self.hasil)
        layout.add_widget(scroll)

        self.content = layout

    def jalankan_analisis(self, *args):
        pw = self.input_pw.text
        ssid = self.input_ssid.text or "(manual)"

        if not pw:
            self.hasil.text = "[color=ff5555]Password kosong.[/color]"
            return

        hasil = analyze(pw, self.kamus_umum)
        brand = guess_brand(ssid)
        default_match = []
        if brand and brand in self.kamus_router:
            for d in self.kamus_router[brand]:
                if pw.lower() == d.lower():
                    default_match.append(d)

        warna = "00cc66" if hasil["score"] >= 80 else \
                "00aaaa" if hasil["score"] >= 60 else \
                "ffcc00" if hasil["score"] >= 40 else "ff5555"

        teks = f"[b]SSID:[/b] {ssid}\n"
        teks += f"[b]Skor:[/b] [color={warna}]{hasil['score']}/100 ({hasil['label']})[/color]\n"
        teks += f"[b]Entropi:[/b] {hasil['entropy']} bit\n"
        teks += f"[b]Panjang:[/b] {hasil['length']} karakter\n\n"

        if hasil["issues"]:
            teks += "[b]Masalah:[/b]\n"
            for i in hasil["issues"]:
                teks += f"  • {i}\n"
        else:
            teks += "[b]Masalah:[/b] tidak ada\n"

        if default_match:
            teks += f"\n[color=ff5555][b]PERINGATAN:[/b] cocok default router — "
            teks += ", ".join(default_match) + "[/color]"

        self.hasil.text = teks


class PopupPesan(Popup):
    def __init__(self, judul, pesan, **kw):
        super().__init__(**kw)
        self.title = judul
        self.size_hint = (0.9, 0.6)
        layout = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        scroll = ScrollView()
        lbl = Label(text=pesan, font_size=dp(14), halign="left", valign="top")
        lbl.bind(
            width=lambda *x: setattr(lbl, 'text_size', (lbl.width, None)),
            texture_size=lambda *x: setattr(lbl, 'height', lbl.texture_size[1])
        )
        scroll.add_widget(lbl)
        layout.add_widget(scroll)
        btn = Button(text="Tutup", size_hint_y=None, height=dp(45))
        btn.bind(on_press=self.dismiss)
        layout.add_widget(btn)
        self.content = layout


class WiFiAuditApp(App):
    def build(self):
        self.title = "WiFi Audit"
        return MenuUtama()


if __name__ == "__main__":
    WiFiAuditApp().run()
