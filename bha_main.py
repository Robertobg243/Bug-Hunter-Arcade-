import pygame
import sys
import random
import math
import array

# Inicializar Pygame y audio de forma segura
pygame.init()
AUDIO_ACTIVO = False
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
    AUDIO_ACTIVO = True
except Exception:
    AUDIO_ACTIVO = False

# Dimensiones iniciales de la ventana
ANCHO = 1100
ALTO = 780

# Ventana redimensionable con soporte completo para minimizar y maximizar
screen = pygame.display.set_mode((ANCHO, ALTO), pygame.RESIZABLE)
pygame.display.set_caption("Bug Hunter Arcade [BHA] - Motor Táctico Integral [Sello H]")

clock = pygame.time.Clock()

# Paleta de colores Neón / Pixel Art
NEGRO = (3, 5, 14)
BLANCO = (240, 245, 250)
AZUL_BANNER = (6, 18, 36)
BORDE_NEON = (0, 210, 255)
VERDE_NEON = (50, 255, 140)
AMARILLO_DRONE = (255, 210, 0)
ORO_HISTORIA = (255, 200, 65)
ROJO_CANGREJO = (255, 45, 75)
MAGENTA_CANGREJO = (220, 40, 180)
AZUL_NAVE = (30, 130, 255)
CELESTE_NAVE = (100, 210, 255)
NARANJA_TELEM = (255, 155, 35)
MORADO_SIGILO = (190, 90, 255)

# Fuentes
fuente_chica = pygame.font.SysFont("Consolas", 13, bold=True)
fuente_normal = pygame.font.SysFont("Consolas", 16, bold=True)
fuente_planeta = pygame.font.SysFont("Consolas", 12, bold=True)
fuente_grande = pygame.font.SysFont("Consolas", 28, bold=True)

# Transmisiones de radio en 2 líneas (ISS + NASA + Tierra como referencia orbital)
TRANSMISIONES_RADIO = [
    ("Tierra",  "ISS / NASA-COM",   "Órbita terrestre vigilada. Sensores captan señales sin origen claro.", "Escudos listos: mantén el sector y protege la Tierra."),
    ("Marte",   "ISS / NASA-TELEM", "Rastreo orbital activo hacia Marte; Tierra sin intrusiones confirmadas.", "Sigue cubriendo el frente mientras analizamos los datos."),
    ("Júpiter", "ISS / NASA-RADAR", "Alta densidad de bioseñales en gigantes gaseosos; enlace estable.", "La ISS mantiene respaldo de escudos mientras contienes el avance."),
    ("Saturno", "ISS / NASA-CTRL",  "Contactos en el sector de Saturno; perímetro terrestre monitoreado.", "Atento a firmas colosales y posibles desvíos hacia la Tierra."),
    ("Neptuno", "ISS / NASA-COM",   "Borde exterior alcanzado; datos de procedencia aún no confirmados.", "Defiende el sistema con todo: la Tierra depende de este bloqueo.")
]

def crear_sonido_radio():
    """Genera un breve pitido de enlace de radio en memoria sin archivos externos."""
    if not AUDIO_ACTIVO:
        return None
    try:
        sample_rate = 22050
        duracion = 0.11
        n_muestras = int(sample_rate * duracion)
        buf = array.array("h")
        for i in range(n_muestras):
            t = i / sample_rate
            envolvente = 1.0 - (i / n_muestras)
            tono = math.sin(2.0 * math.pi * 1180.0 * t)
            estatica = random.uniform(-0.25, 0.25)
            muestra = int((tono * 0.45 + estatica) * envolvente * 9000)
            buf.append(max(-32767, min(32767, muestra)))
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception:
        return None

SONIDO_RADIO = crear_sonido_radio()

def reproducir_radio():
    if SONIDO_RADIO is not None:
        try:
            SONIDO_RADIO.play()
        except Exception:
            pass

def dibujar_sol_pixel(superficie, alto_pantalla, tiempo):
    """Dibuja el Sol gigante completo y sin cortes en estilo Pixel Art con erupciones."""
    factor = 4
    ancho_sol = int(alto_pantalla * 0.42)
    w_p = max(80, ancho_sol // factor)
    h_p = max(120, alto_pantalla // factor)
    
    surf = pygame.Surface((w_p, h_p), pygame.SRCALPHA)
    
    cx = -int(h_p * 0.16)
    cy = h_p // 2
    radio = int(h_p * 0.44)
    
    pulso = int(math.sin(tiempo * 0.06) * 2)
    pygame.draw.circle(surf, (255, 70, 0, 70), (cx, cy), radio + 10 + pulso)
    pygame.draw.circle(surf, (255, 120, 0, 130), (cx, cy), radio + 5)
    
    pygame.draw.circle(surf, (255, 150, 10), (cx, cy), radio)
    pygame.draw.circle(surf, (255, 200, 35), (cx - 3, cy), max(5, radio - 5))
    pygame.draw.circle(surf, (255, 235, 110), (cx - 6, cy), max(5, radio - 12))
    
    desp1 = int(math.sin(tiempo * 0.04) * 3)
    desp2 = int(math.cos(tiempo * 0.03) * 3)
    pygame.draw.circle(surf, (220, 85, 0), (cx + radio - 10, cy - 16 + desp1), 4)
    pygame.draw.circle(surf, (255, 250, 170), (cx + radio - 7, cy + 14 + desp2), 3)
    
    arco_y1 = cy - int(radio * 0.45) + desp1
    arco_x1 = cx + int(math.sqrt(max(0, radio**2 - (arco_y1 - cy)**2))) - 2
    pygame.draw.arc(surf, (255, 190, 40), (arco_x1 - 4, arco_y1 - 8, 12, 16), -1.5, 1.5, 2)

    arco_y2 = cy + int(radio * 0.38) - desp2
    arco_x2 = cx + int(math.sqrt(max(0, radio**2 - (arco_y2 - cy)**2))) - 2
    pygame.draw.arc(surf, (255, 140, 20), (arco_x2 - 4, arco_y2 - 7, 10, 14), -1.5, 1.5, 2)
    
    escalada = pygame.transform.scale(surf, (w_p * factor, h_p * factor))
    superficie.blit(escalada, (0, 0))

def dibujar_iss_pixel(superficie, x, y, tiempo, reparando=False):
    """Dibuja la Estación Espacial Internacional (ISS) viva con indicador de abastecimiento."""
    factor = 3
    surf = pygame.Surface((64, 42), pygame.SRCALPHA)
    
    pygame.draw.rect(surf, (205, 215, 225), (8, 20, 48, 2))
    pygame.draw.rect(surf, (235, 240, 245), (27, 13, 10, 16))
    pygame.draw.rect(surf, (165, 175, 190), (30, 8, 4, 26))
    pygame.draw.rect(surf, (125, 135, 150), (24, 17, 16, 8))
    
    brillo = int(math.sin(tiempo * 0.08) * 25)
    col_izq = (min(255, max(0, 185 + brillo)), min(255, max(0, 145 + brillo)), 100)
    col_der = (85, min(255, max(0, 135 - brillo)), min(255, max(0, 190 - brillo)))

    for px in [10, 17]:
        pygame.draw.rect(surf, (45, 70, 115), (px, 4, 5, 14))
        pygame.draw.rect(surf, col_izq, (px + 1, 5, 3, 12))
        pygame.draw.rect(surf, (45, 70, 115), (px, 24, 5, 14))
        pygame.draw.rect(surf, col_izq, (px + 1, 25, 3, 12))

    for px in [42, 49]:
        pygame.draw.rect(surf, (40, 65, 110), (px, 3, 5, 15))
        pygame.draw.rect(surf, col_der, (px + 1, 4, 3, 13))
        pygame.draw.rect(surf, (40, 65, 110), (px, 24, 5, 15))
        pygame.draw.rect(surf, col_der, (px + 1, 25, 3, 13))

    if reparando:
        col_baliza = VERDE_NEON if (tiempo // 8) % 2 == 0 else (0, 200, 120)
        pygame.draw.rect(surf, col_baliza, (29, 28, 6, 4))
    elif (tiempo // 15) % 2 == 0:
        pygame.draw.rect(surf, (255, 50, 50), (7, 20, 2, 2))
        pygame.draw.rect(surf, (50, 255, 120), (55, 20, 2, 2))
    else:
        pygame.draw.rect(surf, (0, 220, 255), (31, 7, 2, 2))

    escalada = pygame.transform.scale(surf, (64 * factor, 42 * factor))
    ix, iy = int(x), int(y)
    superficie.blit(escalada, (ix, iy))

    color_etiqueta = VERDE_NEON if reparando else (140, 210, 255)
    etiqueta = "ISS [REPARANDO]" if reparando else "EEI / ISS [NASA]"
    txt_iss = fuente_planeta.render(etiqueta, True, color_etiqueta)
    superficie.blit(txt_iss, (ix + (64 * factor)//2 - txt_iss.get_width()//2, iy + 42 * factor + 2))

def generar_sprite_planeta_pixel(tipo, radio, pixel_size=3):
    """Genera una esfera pixelada precisa con detalles realistas por planeta."""
    r_grid = max(5, radio // pixel_size)
    extra_x = (r_grid + 6) if tipo == "saturn" else 2
    w_grid = (r_grid + extra_x) * 2 + 1
    h_grid = (r_grid + 2) * 2 + 1

    surf = pygame.Surface((w_grid * pixel_size, h_grid * pixel_size), pygame.SRCALPHA)
    cx = w_grid // 2
    cy = h_grid // 2

    def put_px(gx, gy, col):
        if 0 <= gx < w_grid and 0 <= gy < h_grid:
            pygame.draw.rect(surf, col, (gx * pixel_size, gy * pixel_size, pixel_size, pixel_size))

    if tipo == "saturn":
        for gx in range(cx - r_grid - 6, cx + r_grid + 7):
            dx = (gx - cx) / max(1.0, (r_grid + 6))
            if abs(dx) <= 1.0:
                y_anillo = cy - int(dx * 2)
                if y_anillo < cy:
                    col_anillo = (155, 140, 105) if abs(dx) > 0.55 else (120, 108, 80)
                    put_px(gx, y_anillo, col_anillo)

    for dy in range(-r_grid, r_grid + 1):
        for dx in range(-r_grid, r_grid + 1):
            dist_sq = dx * dx + dy * dy
            if dist_sq <= r_grid * r_grid:
                gx = cx + dx
                gy = cy + dy
                luz = (-dx * 0.6 - dy * 0.5) / max(1.0, r_grid)
                es_borde_oscuro = (dx + dy * 0.5) > r_grid * 0.65

                if tipo == "mercury":
                    base = (145, 145, 150)
                    if es_borde_oscuro:
                        col = (85, 85, 92)
                    elif (dx * dx + (dy + 1) * (dy + 1)) <= max(1, (r_grid // 3) ** 2):
                        col = (105, 105, 112)
                    elif luz > 0.25:
                        col = (175, 175, 180)
                    else:
                        col = base

                elif tipo == "venus":
                    banda = math.sin(dy * 0.7 + dx * 0.15)
                    if es_borde_oscuro:
                        col = (150, 100, 50)
                    elif banda > 0.35:
                        col = (238, 198, 130)
                    elif banda < -0.35:
                        col = (185, 130, 70)
                    else:
                        col = (215, 165, 98)

                elif tipo == "earth":
                    continente = (dx * 0.8 - dy * 0.6)
                    if dy < -r_grid * 0.68:
                        col = (240, 245, 250)
                    elif -2 <= continente <= 3 and abs(dy) < r_grid * 0.55:
                        col = (195, 155, 85) if abs(dy) < 2 else (60, 165, 80)
                    else:
                        col = (25, 85, 195) if es_borde_oscuro else (45, 125, 230)
                    if (dx + dy) % 7 == 0 and dy > -r_grid * 0.6:
                        col = (235, 242, 250)

                elif tipo == "mars":
                    if es_borde_oscuro:
                        col = (115, 38, 22)
                    elif dy < -r_grid * 0.75:
                        col = (235, 225, 220)
                    elif (dx - 1) ** 2 + (dy + 1) ** 2 <= max(1, (r_grid // 2) ** 2):
                        col = (140, 48, 26)
                    else:
                        col = (205, 82, 48) if luz > 0.15 else (175, 62, 34)

                elif tipo == "jupiter":
                    franja = (dy + r_grid) * 5 // max(1, r_grid * 2)
                    if es_borde_oscuro:
                        col = (120, 82, 54)
                    elif franja in (1, 3):
                        col = (165, 112, 72)
                    elif franja in (0, 2, 4):
                        col = (228, 205, 175)
                    else:
                        col = (190, 145, 105)
                    if ((dx - r_grid // 3) ** 2 + (dy - r_grid // 4) ** 2) <= max(2, (r_grid // 3) ** 2):
                        col = (205, 72, 48)

                elif tipo == "saturn":
                    franja = (dy + r_grid) * 4 // max(1, r_grid * 2)
                    if es_borde_oscuro:
                        col = (155, 135, 95)
                    elif franja % 2 == 0:
                        col = (225, 200, 145)
                    else:
                        col = (198, 172, 118)

                elif tipo == "uranus":
                    if es_borde_oscuro:
                        col = (60, 155, 185)
                    elif luz > 0.2:
                        col = (145, 235, 250)
                    else:
                        col = (95, 205, 228)

                elif tipo == "neptune":
                    if es_borde_oscuro:
                        col = (25, 55, 150)
                    elif (dx + dy * 2) % 6 == 0 and luz > -0.2:
                        col = (150, 200, 255)
                    else:
                        col = (45, 95, 215) if luz > 0.1 else (35, 75, 180)

                else:
                    col = (180, 180, 180)

                put_px(gx, gy, col)

    if tipo == "saturn":
        for gx in range(cx - r_grid - 6, cx + r_grid + 7):
            dx = (gx - cx) / max(1.0, (r_grid + 6))
            if abs(dx) <= 1.0:
                y_anillo = cy - int(dx * 2)
                if y_anillo >= cy:
                    col_anillo = (218, 198, 150) if abs(dx) > 0.45 else (185, 165, 120)
                    put_px(gx, y_anillo, col_anillo)

    return surf

def dibujar_sistema_solar_pixel(superficie, planetas, sprites_planetas, ancho_act, alto_act, tiempo):
    """Dibuja los planetas reales en modo pixel art con movimiento activo y nombres en español."""
    for p in planetas:
        p["x"] += p["vx"]
        p["y"] += p["vy"]

        lim_izq = ancho_act * 0.21
        lim_der = ancho_act - 60
        lim_sup = 115
        lim_inf = alto_act - 135

        if p["x"] < lim_izq:
            p["x"] = lim_izq
            p["vx"] *= -1
        elif p["x"] > lim_der:
            p["x"] = lim_der
            p["vx"] *= -1

        if p["y"] < lim_sup:
            p["y"] = lim_sup
            p["vy"] *= -1
        elif p["y"] > lim_inf:
            p["y"] = lim_inf
            p["vy"] *= -1

        px = int(p["x"])
        py = int(p["y"] + math.sin(tiempo * 0.025 + p["fase"]) * 6)
        surf = sprites_planetas[p["tipo"]]

        superficie.blit(surf, (px - surf.get_width() // 2, py - surf.get_height() // 2))

        col_nom = VERDE_NEON if p["tipo"] == "earth" else BLANCO
        txt = fuente_planeta.render(p["nombre"], True, col_nom)
        superficie.blit(txt, (px - txt.get_width() // 2, py + p["radio"] + 6))

def dibujar_cangrejo_pixel(superficie, x, y, color_cuerpo, tiene_radar):
    """Dibuja los cangrejos enemigos en Pixel Art con radar rojo opcional."""
    factor = 3
    surf = pygame.Surface((16, 14), pygame.SRCALPHA)
    
    pygame.draw.rect(surf, color_cuerpo, (4, 3, 8, 6))
    pygame.draw.rect(surf, color_cuerpo, (2, 5, 12, 3))
    pygame.draw.rect(surf, color_cuerpo, (2, 1, 2, 3))
    pygame.draw.rect(surf, color_cuerpo, (12, 1, 2, 3))
    pygame.draw.rect(surf, color_cuerpo, (1, 8, 2, 3))
    pygame.draw.rect(surf, color_cuerpo, (4, 9, 2, 2))
    pygame.draw.rect(surf, color_cuerpo, (10, 9, 2, 2))
    pygame.draw.rect(surf, color_cuerpo, (13, 8, 2, 3))
    pygame.draw.rect(surf, (255, 230, 0), (5, 5, 2, 2))
    pygame.draw.rect(surf, (255, 230, 0), (9, 5, 2, 2))

    escalada = pygame.transform.scale(surf, (16 * factor, 14 * factor))
    px, py = int(x), int(y)
    superficie.blit(escalada, (px - 24, py - 21))

    if tiene_radar:
        pygame.draw.circle(superficie, (255, 45, 45), (px, py), 28, 2)

def dibujar_dron_secreto_tierra(superficie, dron_sec, tiempo):
    """Dibuja el dron secreto desplegado por la nave nodriza con rumbo a la Tierra."""
    dx, dy = int(dron_sec["x"]), int(dron_sec["y"])
    parpadeo = MORADO_SIGILO if (tiempo // 6) % 2 == 0 else ROJO_CANGREJO
    pygame.draw.polygon(superficie, parpadeo, [(dx, dy - 12), (dx - 11, dy + 8), (dx, dy + 4), (dx + 11, dy + 8)])
    pygame.draw.rect(superficie, BLANCO, (dx - 2, dy - 3, 4, 4))
    pygame.draw.circle(superficie, parpadeo, (dx, dy), 16, 1)

    etiq = fuente_planeta.render("DRON -> TIERRA", True, parpadeo)
    superficie.blit(etiq, (dx - etiq.get_width() // 2, dy + 14))

def dibujar_radar_deteccion_tth(superficie, nodriza, tiempo):
    """Dibuja el escaneo en radar del TTH antes de la aparición colosal de la nave nodriza."""
    rx, ry = int(nodriza["radar_x"]), int(nodriza["radar_y"])
    pulso_r = 22 + int((tiempo * 1.4) % 45)
    pygame.draw.circle(superficie, BORDE_NEON, (rx, ry), pulso_r, 2)
    pygame.draw.circle(superficie, ROJO_CANGREJO, (rx, ry), 14, 2)
    pygame.draw.line(superficie, VERDE_NEON, (rx - 35, ry), (rx + 35, ry), 1)
    pygame.draw.line(superficie, VERDE_NEON, (rx, ry - 35), (rx, ry + 35), 1)

    txt = fuente_planeta.render(f"RADAR TTH: CONTACTO COLOSAL ({nodriza['tam_km']:.1f} KM)", True, AMARILLO_DRONE)
    superficie.blit(txt, (rx - txt.get_width() // 2, ry - 52))

def dibujar_nave_nodriza_colosal_pixel(superficie, nodriza, distancia_km, velocidad_kms, tiempo):
    """Dibuja una Nave Nodriza colosal con diseño acorazado bio-mecánico, alas y reactor central."""
    factor = 5
    surf = pygame.Surface((52, 28), pygame.SRCALPHA)

    pygame.draw.polygon(surf, (55, 65, 85), [(26, 2), (3, 12), (10, 20), (26, 15)])
    pygame.draw.polygon(surf, (55, 65, 85), [(26, 2), (49, 12), (42, 20), (26, 15)])

    pygame.draw.rect(surf, (85, 98, 122), (14, 6, 24, 12))
    pygame.draw.rect(surf, (130, 35, 55), (17, 8, 18, 8))
    for cx_costilla in [19, 25, 31]:
        pygame.draw.rect(surf, (40, 45, 60), (cx_costilla, 7, 2, 10))

    pygame.draw.rect(surf, (175, 185, 200), (4, 12, 3, 7))
    pygame.draw.rect(surf, (175, 185, 200), (45, 12, 3, 7))
    pygame.draw.rect(surf, (195, 205, 220), (21, 18, 3, 6))
    pygame.draw.rect(surf, (195, 205, 220), (28, 18, 3, 6))

    col_core = (255, 60, 90) if (tiempo // 7) % 2 == 0 else (255, 190, 45)
    pygame.draw.rect(surf, col_core, (23, 9, 6, 6))
    pygame.draw.rect(surf, BLANCO, (25, 11, 2, 2))

    pygame.draw.rect(surf, (0, 210, 255), (16, 4, 4, 2))
    pygame.draw.rect(surf, (0, 210, 255), (32, 4, 4, 2))

    escalada = pygame.transform.scale(surf, (52 * factor, 28 * factor))
    nx, ny = int(nodriza["x"]), int(nodriza["y"])
    w_s, h_s = escalada.get_width(), escalada.get_height()
    superficie.blit(escalada, (nx - w_s // 2, ny - h_s // 2))

    barra_w = 200
    barra_h = 10
    bx = nx - barra_w // 2
    by = ny - h_s // 2 - 22
    pct = max(0.0, nodriza["hp"] / nodriza["hp_max"])
    pygame.draw.rect(superficie, (25, 12, 20), (bx, by, barra_w, barra_h))
    pygame.draw.rect(superficie, ROJO_CANGREJO, (bx, by, int(barra_w * pct), barra_h))
    pygame.draw.rect(superficie, BLANCO, (bx, by, barra_w, barra_h), 1)

    t_info = fuente_planeta.render(
        f"COLOSO [{nodriza['tam_km']:.1f} km] | DIST: {distancia_km:.1f} km | VEL: {velocidad_kms:.1f} km/s",
        True,
        AMARILLO_DRONE
    )
    superficie.blit(t_info, (nx - t_info.get_width() // 2, by - 15))

def dibujar_nave_y_drones_pixel(superficie, x, y, drones, reparando=False):
    """Dibuja la nave principal en Pixel Art azul con propulsores, drones y aura de abastecimiento."""
    factor = 3
    surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    
    pygame.draw.polygon(surf, AZUL_NAVE, [(12, 1), (4, 18), (12, 15), (20, 18)])
    pygame.draw.polygon(surf, CELESTE_NAVE, [(12, 3), (8, 15), (12, 13), (16, 15)])
    pygame.draw.rect(surf, (200, 245, 255), (11, 7, 2, 5))
    pygame.draw.rect(surf, (180, 200, 220), (6, 9, 2, 8))
    pygame.draw.rect(surf, (180, 200, 220), (16, 9, 2, 8))
    pygame.draw.rect(surf, (0, 220, 255), (7, 18, 2, 4))
    pygame.draw.rect(surf, (0, 220, 255), (15, 18, 2, 4))
    pygame.draw.rect(surf, BLANCO, (7, 18, 2, 2))
    pygame.draw.rect(surf, BLANCO, (15, 18, 2, 2))

    escalada = pygame.transform.scale(surf, (24 * factor, 24 * factor))
    jx, jy = int(x), int(y)
    superficie.blit(escalada, (jx - 36, jy - 36))

    if reparando:
        pygame.draw.circle(superficie, VERDE_NEON, (jx, jy), 42, 2)

    for d in drones:
        dx = jx + d["offset_x"]
        dy = jy + 8
        s_dron = pygame.Surface((10, 10), pygame.SRCALPHA)
        pygame.draw.polygon(s_dron, AMARILLO_DRONE, [(5, 1), (1, 8), (5, 6), (9, 8)])
        pygame.draw.rect(s_dron, (255, 120, 0), (4, 8, 2, 2))
        esc_dron = pygame.transform.scale(s_dron, (30, 30))
        superficie.blit(esc_dron, (int(dx) - 15, int(dy) - 15))

def dibujar_radio_comunicacion(superficie, radio_msg, ancho_act, alto_act, tiempo):
    """Dibuja un cuadro de comunicación por radio estilo diálogo (máx. 2 líneas) con barra de lectura."""
    if radio_msg["timer"] <= 0:
        return

    w_box = min(640, ancho_act - 60)
    h_box = 82
    x_box = (ancho_act - w_box) // 2
    y_box = alto_act - 170

    caja = pygame.Rect(x_box, y_box, w_box, h_box)
    pygame.draw.rect(superficie, (8, 22, 42), caja)
    pygame.draw.rect(superficie, ORO_HISTORIA, caja, 2)

    panel_r = pygame.Rect(x_box + 8, y_box + 8, 66, h_box - 16)
    pygame.draw.rect(superficie, (4, 12, 24), panel_r)
    pygame.draw.rect(superficie, BORDE_NEON, panel_r, 1)

    ant_x = panel_r.centerx
    ant_y = panel_r.y + 30
    pygame.draw.rect(superficie, CELESTE_NAVE, (ant_x - 8, ant_y - 6, 16, 12), 1)
    pygame.draw.line(superficie, VERDE_NEON, (ant_x, ant_y - 6), (ant_x - 5, ant_y - 14), 2)

    for idx in range(2):
        r_onda = 8 + idx * 6 + (tiempo // 8) % 5
        pygame.draw.arc(superficie, VERDE_NEON, (ant_x + 4, ant_y - r_onda // 2, r_onda, r_onda), -0.8, 0.8, 2)

    txt_radio = fuente_planeta.render("RADIO", True, ORO_HISTORIA)
    superficie.blit(txt_radio, (panel_r.centerx - txt_radio.get_width() // 2, panel_r.bottom - 14))

    x_txt = panel_r.right + 12
    superficie.blit(fuente_chica.render(radio_msg["canal"], True, ORO_HISTORIA), (x_txt, y_box + 8))
    superficie.blit(fuente_chica.render(radio_msg["linea1"], True, BLANCO), (x_txt, y_box + 27))
    superficie.blit(fuente_chica.render(radio_msg["linea2"], True, VERDE_NEON), (x_txt, y_box + 46))

    dur_max = max(1, radio_msg["duracion"])
    pct_tiempo = max(0.0, min(1.0, radio_msg["timer"] / dur_max))
    barra_x = x_txt
    barra_y = y_box + h_box - 12
    barra_w = w_box - (x_txt - x_box) - 12
    pygame.draw.rect(superficie, (20, 35, 55), (barra_x, barra_y, barra_w, 4))
    pygame.draw.rect(superficie, ORO_HISTORIA, (barra_x, barra_y, int(barra_w * pct_tiempo), 4))

def activar_radio(radio_msg, canal, linea1, linea2, duracion=720):
    radio_msg["canal"] = canal
    radio_msg["linea1"] = linea1
    radio_msg["linea2"] = linea2
    radio_msg["duracion"] = duracion
    radio_msg["timer"] = duracion
    reproducir_radio()

def crear_estado_inicial(ancho_act, alto_act):
    """Crea el estado inicial de la partida."""
    planetas = [
        {"nombre": "MERCURIO", "x": ancho_act * 0.24, "y": alto_act * 0.42, "vx": 0.25,  "vy": -0.10, "radio": 15, "tipo": "mercury", "fase": 0.0},
        {"nombre": "VENUS",    "x": ancho_act * 0.32, "y": alto_act * 0.45, "vx": -0.20, "vy": 0.12,  "radio": 21, "tipo": "venus",   "fase": 1.0},
        {"nombre": "TIERRA",   "x": ancho_act * 0.41, "y": alto_act * 0.41, "vx": 0.18,  "vy": 0.09,  "radio": 24, "tipo": "earth",   "fase": 2.0},
        {"nombre": "MARTE",    "x": ancho_act * 0.49, "y": alto_act * 0.46, "vx": -0.22, "vy": -0.11, "radio": 18, "tipo": "mars",    "fase": 3.0},
        {"nombre": "JÚPITER",  "x": ancho_act * 0.60, "y": alto_act * 0.44, "vx": 0.12,  "vy": -0.07, "radio": 42, "tipo": "jupiter", "fase": 4.0},
        {"nombre": "SATURNO",  "x": ancho_act * 0.73, "y": alto_act * 0.47, "vx": -0.14, "vy": 0.08,  "radio": 33, "tipo": "saturn",  "fase": 5.0},
        {"nombre": "URANO",    "x": ancho_act * 0.84, "y": alto_act * 0.42, "vx": 0.16,  "vy": 0.10,  "radio": 24, "tipo": "uranus",  "fase": 6.0},
        {"nombre": "NEPTUNO",  "x": ancho_act * 0.93, "y": alto_act * 0.45, "vx": -0.15, "vy": -0.09, "radio": 23, "tipo": "neptune", "fase": 7.0},
    ]

    sprites_planetas = {
        p["tipo"]: generar_sprite_planeta_pixel(p["tipo"], p["radio"], pixel_size=3)
        for p in planetas
    }

    nodriza = {
        "estado": "inactiva",
        "radar_timer": 0,
        "radar_x": ancho_act * 0.65,
        "radar_y": 135.0,
        "x": ancho_act * 0.65,
        "y": -90.0,
        "prev_x": ancho_act * 0.65,
        "prev_y": -90.0,
        "vx": 2.4,
        "vy": 0.9,
        "hp": 160,
        "hp_max": 160,
        "oleada": 1,
        "tam_km": 14.8,
        "dron_cooldown": 150
    }

    radio_msg = {
        "timer": 720,
        "duracion": 720,
        "canal": TRANSMISIONES_RADIO[0][1],
        "linea1": TRANSMISIONES_RADIO[0][2],
        "linea2": TRANSMISIONES_RADIO[0][3]
    }
    reproducir_radio()

    return {
        "jugador_x": ancho_act // 2,
        "jugador_y": alto_act - 155,
        "balas_jugador": [],
        "balas_enemigas": [],
        "bugs": [],
        "drones_secretos": [],
        "planetas": planetas,
        "sprites_planetas": sprites_planetas,
        "iss_x": ancho_act * 0.72,
        "iss_y": 85.0,
        "iss_vx": -0.45,
        "nodriza": nodriza,
        "distancia_km": 0.0,
        "velocidad_kms": 0.0,
        "vidas": 2,
        "bajas": 90,
        "escudo": 65,
        "objetivo_actual": 25,
        "objetivo_meta": 25,
        "fase_num": 1,
        "fase_nombre": TRANSMISIONES_RADIO[0][0],
        "radio_msg": radio_msg,
        "logs_tth": [
            "[PILOTO] Bug aniquilado /",
            "[DRON] Bug aniquilado"
        ],
        "ultimo_log_iss": 0,
        "game_over": False,
        "motivo_game_over": ""
    }

def main():
    global screen

    ancho_ini, alto_ini = screen.get_size()
    estrellas = [
        [random.randint(0, ancho_ini), random.randint(0, alto_ini), random.uniform(0.3, 1.4), random.choice([(255,255,255), (180,210,255), (255,230,190)])]
        for _ in range(180)
    ]
    drones = [{"offset_x": -65}, {"offset_x": 65}]

    estado = crear_estado_inicial(ancho_ini, alto_ini)
    tiempo = 0

    while True:
        ancho_act, alto_act = screen.get_size()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((evento.w, evento.h), pygame.RESIZABLE)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and estado["game_over"]:
                    estado = crear_estado_inicial(ancho_act, alto_act)
                    continue
                elif evento.key == pygame.K_SPACE and not estado["game_over"]:
                    estado["balas_jugador"].append([estado["jugador_x"] - 16, estado["jugador_y"] - 32, 0])
                    estado["balas_jugador"].append([estado["jugador_x"] + 16, estado["jugador_y"] - 32, 0])

        if not estado["game_over"]:
            tiempo += 1

            if estado["radio_msg"]["timer"] > 0:
                estado["radio_msg"]["timer"] -= 1

            # --- AUTOMATIZACIÓN DE MOVIMIENTO DE LA NAVE (IZQ, DER, DELANTE, ATRÁS) ---
            centro_x = ancho_act * 0.55
            amplitud_x = ancho_act * 0.28
            estado["jugador_x"] = centro_x + math.sin(tiempo * 0.032) * amplitud_x
            estado["jugador_y"] = (alto_act - 165) + math.cos(tiempo * 0.024) * 45

            # --- MOVIMIENTO ORBITAL DE LA ISS ---
            estado["iss_x"] += estado["iss_vx"]
            estado["iss_y"] = 82 + math.sin(tiempo * 0.015) * 10
            if estado["iss_x"] < ancho_act * 0.25:
                estado["iss_x"] = ancho_act * 0.25
                estado["iss_vx"] *= -1
            elif estado["iss_x"] > ancho_act - 210:
                estado["iss_x"] = ancho_act - 210
                estado["iss_vx"] *= -1

            # --- ROL DE LA ISS: ABASTECIMIENTO Y REPARACIÓN DE ESCUDO ---
            centro_iss_x = estado["iss_x"] + 96
            centro_iss_y = estado["iss_y"] + 63
            distancia_iss = math.hypot(centro_iss_x - estado["jugador_x"], centro_iss_y - estado["jugador_y"])
            reparando_escudo = (estado["escudo"] < 100) and (distancia_iss < 560)

            if reparando_escudo and tiempo % 8 == 0:
                estado["escudo"] = min(100, estado["escudo"] + 2)
                if tiempo - estado["ultimo_log_iss"] > 90:
                    estado["ultimo_log_iss"] = tiempo
                    estado["logs_tth"].append("[ISS-BASE] Escudo abastecido")
                    if len(estado["logs_tth"]) > 4:
                        estado["logs_tth"].pop(0)

            nodriza = estado["nodriza"]

            # --- PASO 1: ACTIVAR RADAR TTH AL COMPLETAR EL OBJETIVO ---
            if nodriza["estado"] == "inactiva" and estado["objetivo_actual"] >= estado["objetivo_meta"]:
                nodriza["estado"] = "radar"
                nodriza["radar_timer"] = 90
                nodriza["radar_x"] = ancho_act * 0.62
                nodriza["radar_y"] = 145.0
                nodriza["tam_km"] = round(14.8 + (nodriza["oleada"] - 1) * 3.4, 1)
                activar_radio(
                    estado["radio_msg"],
                    "ISS / NASA-RADAR",
                    f"Firma colosal de {nodriza['tam_km']} km detectada en radar.",
                    "Atención al sector: la nave nodriza entra en posición.",
                    duracion=660
                )

            # --- PASO 2: ESCANEO EN RADAR ANTES DE LA APARICIÓN COLOSAL ---
            if nodriza["estado"] == "radar":
                nodriza["radar_timer"] -= 1
                nodriza["radar_x"] = ancho_act * 0.62 + math.cos(tiempo * 0.05) * 55
                nodriza["radar_y"] = 145.0 + math.sin(tiempo * 0.04) * 18
                estado["distancia_km"] = round(math.hypot(nodriza["radar_x"] - estado["jugador_x"], nodriza["radar_y"] - estado["jugador_y"]) * 0.18, 1)
                estado["velocidad_kms"] = round(18.5 + abs(math.cos(tiempo * 0.05)) * 14.0, 1)

                if nodriza["radar_timer"] <= 0:
                    nodriza["estado"] = "colosal"
                    nodriza["x"] = nodriza["radar_x"]
                    nodriza["y"] = -110.0
                    nodriza["prev_x"] = nodriza["x"]
                    nodriza["prev_y"] = nodriza["y"]
                    nodriza["vx"] = 2.5
                    nodriza["vy"] = 1.1
                    nodriza["hp_max"] = 160 + (nodriza["oleada"] - 1) * 45
                    nodriza["hp"] = nodriza["hp_max"]
                    nodriza["dron_cooldown"] = 150
                    estado["logs_tth"].append("[TTH-ALERTA] Entidad colosal en sector")
                    if len(estado["logs_tth"]) > 4:
                        estado["logs_tth"].pop(0)

            # --- PASO 3: MOVIMIENTO DINÁMICO Y TELEMETRÍA TTH DE LA NAVE NODRIZA COLOSAL ---
            if nodriza["estado"] == "colosal":
                nodriza["prev_x"] = nodriza["x"]
                nodriza["prev_y"] = nodriza["y"]

                lim_izq_n = ancho_act * 0.30 + 110
                lim_der_n = ancho_act - 135
                lim_sup_n = 115
                lim_inf_n = max(210, int(alto_act * 0.36))

                if nodriza["y"] < lim_sup_n + 20:
                    nodriza["y"] += 2.4
                    nodriza["x"] += math.sin(tiempo * 0.04) * 2.2
                else:
                    aceleracion = 1.0 + 0.35 * math.sin(tiempo * 0.025)
                    nodriza["x"] += nodriza["vx"] * aceleracion
                    nodriza["y"] += nodriza["vy"] + math.cos(tiempo * 0.035) * 1.15

                    if nodriza["x"] < lim_izq_n:
                        nodriza["x"] = lim_izq_n
                        nodriza["vx"] = abs(nodriza["vx"])
                    elif nodriza["x"] > lim_der_n:
                        nodriza["x"] = lim_der_n
                        nodriza["vx"] = -abs(nodriza["vx"])

                    if nodriza["y"] < lim_sup_n:
                        nodriza["y"] = lim_sup_n
                        nodriza["vy"] = abs(nodriza["vy"])
                    elif nodriza["y"] > lim_inf_n:
                        nodriza["y"] = lim_inf_n
                        nodriza["vy"] = -abs(nodriza["vy"])

                dx_n = nodriza["x"] - estado["jugador_x"]
                dy_n = nodriza["y"] - estado["jugador_y"]
                estado["distancia_km"] = round(math.hypot(dx_n, dy_n) * 0.16, 1)

                vel_px = math.hypot(nodriza["x"] - nodriza["prev_x"], nodriza["y"] - nodriza["prev_y"])
                estado["velocidad_kms"] = round(vel_px * 6.8, 1)

                # Despliegue secreto de un dron con rumbo a la Tierra (equilibrado para ~40% de éxito)
                nodriza["dron_cooldown"] -= 1
                if nodriza["dron_cooldown"] <= 0 and len(estado["drones_secretos"]) < 1:
                    nodriza["dron_cooldown"] = 320
                    rumbo_x = random.choice([-0.55, 0.0, 0.55])
                    estado["drones_secretos"].append({
                        "x": nodriza["x"],
                        "y": nodriza["y"] + 42,
                        "vx": rumbo_x,
                        "vy": 2.25
                    })
                    activar_radio(
                        estado["radio_msg"],
                        "ISS / NASA-ALERTA",
                        "Dron secreto desplegado por la nodriza con rumbo a la Tierra.",
                        "Si alcanza la órbita terrestre, la misión cae. ¡Intercepta!",
                        duracion=720
                    )

                if tiempo % 65 == 0:
                    for offset in (-42, -14, 14, 42):
                        estado["balas_enemigas"].append([nodriza["x"] + offset, nodriza["y"] + 45])

                if tiempo % 145 == 0 and len(estado["bugs"]) < 8:
                    estado["bugs"].append([nodriza["x"], nodriza["y"] + 48, ROJO_CANGREJO, True, random.choice([-1.8, 1.8])])

            # Actualizar drones secretos rumbo a la Tierra
            for ds in estado["drones_secretos"][:]:
                ds["x"] += ds["vx"] + math.sin(tiempo * 0.06) * 0.45
                ds["y"] += ds["vy"]
                if ds["x"] < ancho_act * 0.24:
                    ds["x"] = ancho_act * 0.24
                    ds["vx"] = abs(ds["vx"])
                elif ds["x"] > ancho_act - 60:
                    ds["x"] = ancho_act - 60
                    ds["vx"] = -abs(ds["vx"])

                if ds["y"] >= alto_act - 102:
                    estado["game_over"] = True
                    estado["motivo_game_over"] = "DRON SECRETO INFILTRADO EN LA TIERRA - PULSA ENTER PARA REINICIAR"
                    break

            # Generar cangrejos enemigos
            intervalo_bug = 75 if nodriza["estado"] == "colosal" else 42
            max_bugs = 6 if nodriza["estado"] == "colosal" else 12
            if tiempo % intervalo_bug == 0 and len(estado["bugs"]) < max_bugs:
                bx = random.randint(int(ancho_act * 0.26), int(ancho_act * 0.88))
                by = random.randint(80, 140)
                color = random.choice([ROJO_CANGREJO, MAGENTA_CANGREJO])
                radar = random.choice([True, False])
                vel_x = random.choice([-1.5, 1.5])
                estado["bugs"].append([bx, by, color, radar, vel_x])

            # Drones disparan automáticamente en apoyo
            if tiempo % 22 == 0 and (estado["bugs"] or nodriza["estado"] == "colosal"):
                for d in drones:
                    estado["balas_jugador"].append([estado["jugador_x"] + d["offset_x"], estado["jugador_y"] - 10, 1])

            # Enemigos cangrejos avanzan y atacan
            for bg in estado["bugs"][:]:
                bg[0] += bg[4]
                bg[1] += 1.3
                if bg[0] < ancho_act * 0.24 or bg[0] > ancho_act - 60:
                    bg[4] *= -1
                if random.random() < 0.008:
                    estado["balas_enemigas"].append([bg[0], bg[1] + 20])
                if bg[1] > alto_act - 100:
                    estado["bugs"].remove(bg)

            # Actualizar balas del jugador y drones
            for b in estado["balas_jugador"][:]:
                b[1] -= 13
                if b[1] < 65:
                    estado["balas_jugador"].remove(b)

            # Actualizar balas enemigas
            for be in estado["balas_enemigas"][:]:
                be[1] += 6
                if abs(be[0] - estado["jugador_x"]) < 28 and abs(be[1] - estado["jugador_y"]) < 28:
                    estado["balas_enemigas"].remove(be)
                    estado["escudo"] = max(10, estado["escudo"] - 5)
                elif be[1] > alto_act - 85:
                    estado["balas_enemigas"].remove(be)

            # Colisiones balas del piloto vs drones secretos a la Tierra
            for b in estado["balas_jugador"][:]:
                if b[2] != 0:
                    continue
                for ds in estado["drones_secretos"][:]:
                    if abs(b[0] - ds["x"]) < 28 and abs(b[1] - ds["y"]) < 26:
                        if b in estado["balas_jugador"]:
                            estado["balas_jugador"].remove(b)
                        if ds in estado["drones_secretos"]:
                            estado["drones_secretos"].remove(ds)
                        estado["bajas"] += 5
                        estado["logs_tth"].append("[TTH-OK] Dron a Tierra interceptado")
                        if len(estado["logs_tth"]) > 4:
                            estado["logs_tth"].pop(0)
                        break

            # Colisiones balas vs Nave Nodriza Colosal
            if nodriza["estado"] == "colosal":
                for b in estado["balas_jugador"][:]:
                    if abs(b[0] - nodriza["x"]) < 105 and abs(b[1] - nodriza["y"]) < 55:
                        estado["balas_jugador"].remove(b)
                        danio = 2 if b[2] == 0 else 1
                        nodriza["hp"] -= danio
                        if nodriza["hp"] <= 0:
                            nodriza["estado"] = "inactiva"
                            nodriza["oleada"] += 1
                            estado["drones_secretos"].clear()
                            estado["bajas"] += 15
                            estado["objetivo_actual"] = 0
                            estado["fase_num"] += 1
                            idx_cap = (estado["fase_num"] - 1) % len(TRANSMISIONES_RADIO)
                            estado["fase_nombre"] = TRANSMISIONES_RADIO[idx_cap][0]
                            activar_radio(
                                estado["radio_msg"],
                                TRANSMISIONES_RADIO[idx_cap][1],
                                TRANSMISIONES_RADIO[idx_cap][2],
                                TRANSMISIONES_RADIO[idx_cap][3],
                                duracion=720
                            )
                            estado["logs_tth"].append("[TTH-OK] Coloso neutralizado")
                            if len(estado["logs_tth"]) > 4:
                                estado["logs_tth"].pop(0)
                        break

            # Colisiones balas vs cangrejos
            for b in estado["balas_jugador"][:]:
                for bg in estado["bugs"][:]:
                    if abs(b[0] - bg[0]) < 26 and abs(b[1] - bg[1]) < 24:
                        if b in estado["balas_jugador"]:
                            estado["balas_jugador"].remove(b)
                        if bg in estado["bugs"]:
                            estado["bugs"].remove(bg)
                        estado["bajas"] += 1
                        if nodriza["estado"] == "inactiva" and estado["objetivo_actual"] < estado["objetivo_meta"]:
                            estado["objetivo_actual"] += 1
                        origen = "DRON" if b[2] == 1 else "PILOTO"
                        estado["logs_tth"].append(f"[{origen}] Bug aniquilado")
                        if len(estado["logs_tth"]) > 4:
                            estado["logs_tth"].pop(0)
                        break

        # ================= RENDERIZADO =================
        screen.fill(NEGRO)

        for est in estrellas:
            if not estado["game_over"]:
                est[1] += est[2]
                if est[1] > alto_act:
                    est[1] = 60
                    est[0] = random.randint(0, ancho_act)
            pygame.draw.rect(screen, est[3], (int(est[0]), int(est[1]), 2, 2))

        dibujar_sol_pixel(screen, alto_act, tiempo)
        dibujar_sistema_solar_pixel(screen, estado["planetas"], estado["sprites_planetas"], ancho_act, alto_act, tiempo)

        centro_iss_x = estado["iss_x"] + 96
        centro_iss_y = estado["iss_y"] + 63
        distancia_iss = math.hypot(centro_iss_x - estado["jugador_x"], centro_iss_y - estado["jugador_y"])
        reparando_escudo = (estado["escudo"] < 100) and (distancia_iss < 560)

        if reparando_escudo:
            pygame.draw.line(screen, VERDE_NEON, (int(centro_iss_x), int(centro_iss_y)), (int(estado["jugador_x"]), int(estado["jugador_y"])), 2)
            for i in range(1, 5):
                t_p = ((tiempo * 0.05) + i * 0.25) % 1.0
                px_h = int(centro_iss_x + (estado["jugador_x"] - centro_iss_x) * t_p)
                py_h = int(centro_iss_y + (estado["jugador_y"] - centro_iss_y) * t_p)
                pygame.draw.rect(screen, VERDE_NEON, (px_h - 3, py_h - 3, 6, 6))

        dibujar_iss_pixel(screen, estado["iss_x"], estado["iss_y"], tiempo, reparando=reparando_escudo)

        nodriza = estado["nodriza"]
        if nodriza["estado"] == "radar":
            dibujar_radar_deteccion_tth(screen, nodriza, tiempo)
        elif nodriza["estado"] == "colosal":
            dibujar_nave_nodriza_colosal_pixel(screen, nodriza, estado["distancia_km"], estado["velocidad_kms"], tiempo)

        for ds in estado["drones_secretos"]:
            dibujar_dron_secreto_tierra(screen, ds, tiempo)

        for bg in estado["bugs"]:
            dibujar_cangrejo_pixel(screen, bg[0], bg[1], bg[2], bg[3])

        for be in estado["balas_enemigas"]:
            pygame.draw.rect(screen, (255, 60, 60), (int(be[0]) - 2, int(be[1]), 4, 10))

        for b in estado["balas_jugador"]:
            if b[2] == 0:
                pygame.draw.rect(screen, (120, 230, 255), (int(b[0]) - 2, int(b[1]), 4, 18))
                pygame.draw.rect(screen, BLANCO, (int(b[0]) - 1, int(b[1]), 2, 18))
            else:
                pygame.draw.rect(screen, AMARILLO_DRONE, (int(b[0]) - 2, int(b[1]), 3, 12))

        dibujar_nave_y_drones_pixel(screen, estado["jugador_x"], estado["jugador_y"], drones, reparando=reparando_escudo)

        # Cuadro de comunicación por radio estilo diálogo (máx. 2 líneas + barra de lectura)
        dibujar_radio_comunicacion(screen, estado["radio_msg"], ancho_act, alto_act, tiempo)

        # ================= BANNERS ESTILO NOTICIERO =================
        b_sup = pygame.Rect(8, 8, ancho_act - 16, 44)
        pygame.draw.rect(screen, AZUL_BANNER, b_sup)
        pygame.draw.rect(screen, BORDE_NEON, b_sup, 2)

        screen.blit(fuente_normal.render("FASE:", True, BLANCO), (20, 21))
        screen.blit(fuente_normal.render(f"{estado['fase_nombre']} ({estado['fase_num']})", True, VERDE_NEON), (72, 21))
        screen.blit(fuente_normal.render(f"| OBJETIVO: {estado['objetivo_actual']}/{estado['objetivo_meta']} | VIDAS:", True, BLANCO), (190, 21))

        for i in range(3):
            cx = 485 + i * 24
            col_c = (230, 45, 65) if i < estado["vidas"] else (75, 85, 95)
            pygame.draw.circle(screen, col_c, (cx - 4, 27), 5)
            pygame.draw.circle(screen, col_c, (cx + 4, 27), 5)
            pygame.draw.polygon(screen, col_c, [(cx - 9, 29), (cx + 9, 29), (cx, 38)])

        screen.blit(fuente_normal.render("| ESCUDO:", True, BLANCO), (560, 21))
        pygame.draw.rect(screen, (20, 45, 75), (655, 22, 130, 16))
        col_barra = VERDE_NEON if reparando_escudo else BORDE_NEON
        pygame.draw.rect(screen, col_barra, (655, 22, int(130 * (estado["escudo"] / 100)), 16))
        pygame.draw.rect(screen, BLANCO, (655, 22, 130, 16), 1)

        screen.blit(fuente_normal.render(f"| BAJAS: {estado['bajas']}", True, BLANCO), (800, 21))

        mitad = (ancho_act - 24) // 2
        b_inf_izq = pygame.Rect(8, alto_act - 78, mitad, 70)
        b_inf_der = pygame.Rect(mitad + 16, alto_act - 78, mitad, 70)

        pygame.draw.rect(screen, AZUL_BANNER, b_inf_izq)
        pygame.draw.rect(screen, BORDE_NEON, b_inf_izq, 2)

        pygame.draw.rect(screen, AZUL_BANNER, b_inf_der)
        pygame.draw.rect(screen, BORDE_NEON, b_inf_der, 2)

        logs_tth = estado["logs_tth"]
        screen.blit(fuente_chica.render("TTH TERMINAL - SHIELD LOG:", True, VERDE_NEON), (20, alto_act - 70))
        screen.blit(fuente_chica.render(f"{logs_tth[-2]} /" if len(logs_tth) > 1 else "", True, BLANCO), (20, alto_act - 50))
        screen.blit(fuente_chica.render(logs_tth[-1], True, BLANCO), (20, alto_act - 32))

        x_der = mitad + 28
        screen.blit(fuente_chica.render("DEBUG LOG:", True, VERDE_NEON), (x_der, alto_act - 70))

        if nodriza["estado"] in ("radar", "colosal"):
            linea_telem = (
                f"TTH-TELEM: {nodriza['tam_km']:.1f}km | DIST:{estado['distancia_km']:.1f}km | VEL:{estado['velocidad_kms']:.1f}km/s"
            )
            screen.blit(fuente_chica.render(linea_telem, True, NARANJA_TELEM), (x_der, alto_act - 50))
        else:
            screen.blit(fuente_chica.render(f"TTH-SHIELD: ACTIVE | RADAR: BUSCANDO | ESCUDO: {estado['escudo']}%", True, BLANCO), (x_der, alto_act - 50))

        estado_sigilo = f"DRON TIERRA: {len(estado['drones_secretos'])} ACTIVO" if estado["drones_secretos"] else "AUTOMATIZACIÓN: ACTIVA (IZQ, DER, DELANTE)"
        color_sigilo = ROJO_CANGREJO if estado["drones_secretos"] else AMARILLO_DRONE
        screen.blit(fuente_chica.render(estado_sigilo, True, color_sigilo), (x_der, alto_act - 32))

        # Cartel de Game Over esperando ENTER para reiniciar desde cero
        if estado["game_over"]:
            panel_go = pygame.Rect(ancho_act // 2 - 350, alto_act // 2 - 60, 700, 120)
            pygame.draw.rect(screen, (18, 6, 14), panel_go)
            pygame.draw.rect(screen, ROJO_CANGREJO, panel_go, 3)
            txt_go = fuente_grande.render("GAME OVER", True, ROJO_CANGREJO)
            txt_mot = fuente_chica.render(estado["motivo_game_over"], True, BLANCO)
            txt_ent = fuente_chica.render("[ ENTER ] REINICIAR MISIÓN", True, VERDE_NEON)
            screen.blit(txt_go, (panel_go.centerx - txt_go.get_width() // 2, panel_go.y + 16))
            screen.blit(txt_mot, (panel_go.centerx - txt_mot.get_width() // 2, panel_go.y + 56))
            screen.blit(txt_ent, (panel_go.centerx - txt_ent.get_width() // 2, panel_go.y + 84))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()