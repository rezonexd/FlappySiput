import pygame
import random
import sys
import os
import time

pygame.init()
pygame.mixer.init()

# Setup layar full
info = pygame.display.Info()
lebar, tinggi = info.current_w, info.current_h
layar = pygame.display.set_mode((lebar, tinggi))
pygame.display.set_caption("Flappy Bird Android")

# Warna
PUTIH = (255, 255, 255)
HITAM = (0, 0, 0)
MERAH = (200, 50, 50)
HIJAU = (50, 200, 50)

# Burung
burung_x = lebar // 3
burung_y = tinggi // 2
kecepatan_terbang = -16
gravitasi = 0.9
kecepatan = 0

# Pipa
jarak_pipa = 400
lebar_pipa = 100
pipa_jarak_horizontal = 500
pipa_list = []

# Skor
skor = 0
highscore = 0
font = pygame.font.SysFont("Times New Roman", 80)
small_font = pygame.font.SysFont("Times New Roman", 50)

# Power-up 2x skor
double_score = False
double_start_time = 0
double_duration = 10  # detik

clock = pygame.time.Clock()

# === Load Aset ===
bg_img = pygame.image.load("assets/background.png")
bg_img = pygame.transform.scale(bg_img, (lebar, tinggi))

bird_img = pygame.image.load("assets/bird.png")
bird_img = pygame.transform.scale(bird_img, (80, 80))

pipe_img = pygame.image.load("assets/pipe.png")
pipe_img = pygame.transform.scale(pipe_img, (lebar_pipa, tinggi))

pipe_x2_img = pygame.image.load("assets/pipe_x2.png")
pipe_x2_img = pygame.transform.scale(pipe_x2_img, (lebar_pipa, tinggi))

popup_x2 = pygame.image.load("assets/x2.png")
popup_x2 = pygame.transform.scale(popup_x2, (400, 200))  # popup di tengah

# Base / tanah
try:
    base_img = pygame.image.load("assets/base.png")
    base_height = 120
    base_img = pygame.transform.scale(base_img, (lebar, base_height))
    use_base = True
except:
    base_height = 120
    use_base = False

# Background menu
menu_bg = pygame.image.load("assets/menu/menu_bg.png")
menu_bg = pygame.transform.scale(menu_bg, (lebar, tinggi))

# === Suara ===
backsound = "assets/sounds/backsound.mp3"
flap_sound = pygame.mixer.Sound("assets/sounds/flap.mp3")
hit_sound = pygame.mixer.Sound("assets/sounds/hit.mp3")

pygame.mixer.music.load(backsound)
pygame.mixer.music.set_volume(0.4)

# === Database skor ===
db_file = "assets/database/highscore.txt"
if not os.path.exists(db_file):
    with open(db_file, "w") as f:
        f.write("0")

with open(db_file, "r") as f:
    try:
        highscore = int(f.read())
    except:
        highscore = 0

def simpan_highscore(nilai):
    global highscore
    if nilai > highscore:
        highscore = nilai
        with open(db_file, "w") as f:
            f.write(str(highscore))

# === Fungsi Game ===
def buat_pipa():
    tinggi_atas = random.randint(100, tinggi - jarak_pipa - 200)
    jenis = "normal"
    if random.random() < 0.2:  # 20% kemungkinan pipa spesial muncul
        jenis = "x2"
    return [lebar, tinggi_atas, jenis]

def gambar_burung(y):
    layar.blit(bird_img, (burung_x - bird_img.get_width()//2,
                          int(y) - bird_img.get_height()//2))

def gambar_pipa(pipes):
    for px, py, jenis in pipes:
        if jenis == "x2":
            p_img = pipe_x2_img
        else:
            p_img = pipe_img
        pipa_atas = pygame.transform.flip(p_img, False, True)
        layar.blit(pipa_atas, (px, py - tinggi))
        layar.blit(p_img, (px, py + jarak_pipa))

def deteksi_tabrak(b_y, pipes):
    burung_rect = bird_img.get_rect(center=(burung_x, int(b_y)))
    if b_y <= 0 or b_y >= tinggi - base_height:
        return True
    for px, py, jenis in pipes:
        atas_rect = pygame.Rect(px, 0, lebar_pipa, py)
        bawah_rect = pygame.Rect(px, py + jarak_pipa, lebar_pipa, tinggi)
        if burung_rect.colliderect(atas_rect) or burung_rect.colliderect(bawah_rect):
            return True
    return False

def tampilkan_skor(skor):
    teks = font.render(f"Skor: {skor}", True, PUTIH)
    layar.blit(teks, (20, 20))
    hs_teks = small_font.render(f"Highscore: {highscore}", True, PUTIH)
    layar.blit(hs_teks, (20, 120))

# === Menu Utama ===
def menu():
    tombol_mulai = pygame.Rect(lebar//2 - 150, tinggi//2 - 100, 300, 80)
    tombol_keluar = pygame.Rect(lebar//2 - 150, tinggi//2 + 20, 300, 80)

    while True:
        layar.blit(menu_bg, (0, 0))
        judul = font.render("Flappy Bird by Gx Dikzz", True, PUTIH)
        layar.blit(judul, (lebar//2 - judul.get_width()//2, tinggi//4))

        pygame.draw.rect(layar, HIJAU, tombol_mulai)
        pygame.draw.rect(layar, MERAH, tombol_keluar)

        teks_mulai = small_font.render("MULAI", True, PUTIH)
        teks_keluar = small_font.render("KELUAR", True, PUTIH)

        layar.blit(teks_mulai, (tombol_mulai.centerx - teks_mulai.get_width()//2,
                               tombol_mulai.centery - teks_mulai.get_height()//2))
        layar.blit(teks_keluar, (tombol_keluar.centerx - teks_keluar.get_width()//2,
                                tombol_keluar.centery - teks_keluar.get_height()//2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_mulai.collidepoint(event.pos):
                    return  # keluar menu -> mulai game
                elif tombol_keluar.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        clock.tick(30)

# === Game Loop ===
def main_game():
    global skor, burung_y, kecepatan, pipa_list, double_score, double_start_time

    skor = 0
    burung_y = tinggi // 2
    kecepatan = 0
    pipa_list = [buat_pipa()]
    double_score = False

    pygame.mixer.music.play(-1)

    jalan = True
    while jalan:
        layar.blit(bg_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                simpan_highscore(skor)
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                kecepatan = kecepatan_terbang
                flap_sound.play()

        kecepatan += gravitasi
        burung_y += kecepatan

        # Gerak pipa
        for i in range(len(pipa_list)):
            pipa_list[i][0] -= 5
        if pipa_list[-1][0] < lebar - pipa_jarak_horizontal:
            pipa_list.append(buat_pipa())
        if pipa_list[0][0] + lebar_pipa < 0:
            _, _, jenis = pipa_list.pop(0)
            if jenis == "x2":
                double_score = True
                double_start_time = time.time()
            skor += 2 if double_score else 1

        gambar_burung(burung_y)
        gambar_pipa(pipa_list)

        if use_base:
            layar.blit(base_img, (0, tinggi - base_height))
        else:
            pygame.draw.rect(layar, (200, 150, 100), (0, tinggi - base_height, lebar, base_height))

        tampilkan_skor(skor)

        # Efek popup 2x skor
        if double_score:
            layar.blit(popup_x2, (lebar//2 - popup_x2.get_width()//2,
                                   tinggi//2 - popup_x2.get_height()//2))
            if time.time() - double_start_time > double_duration:
                double_score = False

        if deteksi_tabrak(burung_y, pipa_list):
            hit_sound.play()
            simpan_highscore(skor)
            pygame.time.delay(1500)
            return  # balik ke menu

        pygame.display.update()
        clock.tick(30)

# === Jalankan ===
while True:
    menu()
    main_game()
    