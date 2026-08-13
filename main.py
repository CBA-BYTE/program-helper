import math
import random
import sys

import pygame

from code_engine import CodeEngine
from database import DatabaseService


class Player:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_strength = 13
        self.on_ground = False
        self.energy = 100

    def move_right(self, steps: int = 1):
        self.rect.x += steps * self.speed * 2
        self.vx = self.speed * 2

    def move_left(self, steps: int = 1):
        self.rect.x -= steps * self.speed * 2
        self.vx = -self.speed * 2

    def jump(self):
        if self.on_ground:
            self.vy = -self.jump_strength
            self.on_ground = False

    def boost(self, amount: int = 1):
        self.rect.x += amount * 40

    def teleport(self, x: int, y: int):
        self.rect.x = x
        self.rect.y = y


class Door:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 28, 74)
        self.is_locked = True

    def unlock(self):
        self.is_locked = False


class Portal:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 52, 70)
        self.active = True


class Particle:
    def __init__(self, x: int, y: int, color, velocity_scale: float = 1.0):
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-2.5, 2.5) * velocity_scale
        self.vy = random.uniform(-3.0, 0.8) * velocity_scale
        self.color = color
        self.life = random.uniform(18, 36)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= 1

    def draw(self, surface):
        alpha = max(0, min(255, int(self.life * 6)))
        particle = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle, (*self.color, alpha), (self.size, self.size), self.size)
        surface.blit(particle, (int(self.x), int(self.y)))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((980, 640))
        pygame.display.set_caption("Code Platformer: Neon Run")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Consolas", 16)
        self.font_small = pygame.font.SysFont("Consolas", 12)
        self.running = True

        self.db = DatabaseService()
        self.student = self.db.get_or_create_student("Alex")
        self.engine = CodeEngine()

        self.player = Player(90, 420)
        self.door = Door(740, 470)
        self.portal = Portal(850, 470)
        self.world = {
            "player": self.player,
            "door": self.door,
            "db": self.db,
            "student": self.student,
            "game": self,
            "portal": self.portal,
        }

        self.platforms = [
            pygame.Rect(0, 560, 980, 80),
            pygame.Rect(180, 470, 180, 18),
            pygame.Rect(470, 420, 180, 18),
            pygame.Rect(620, 360, 170, 18),
        ]

        self.terminal_open = False
        self.input_text = ""
        self.console_output = "Type code to interact. Press ` to toggle the terminal."
        self.command_history = []
        self.particles = []
        self.background_scroll = 0

    def spawn_particles(self, x: int, y: int, color, amount: int = 10):
        for _ in range(amount):
            self.particles.append(Particle(x, y, color, random.uniform(0.6, 1.4)))

    def apply_code(self):
        code = self.input_text.strip()
        if not code:
            return

        if code.upper().startswith(("SELECT", "UPDATE", "INSERT", "DELETE")):
            result = self.engine.execute_sql(code)
        else:
            result = self.engine.execute_python_oop(code, self.world)

        self.console_output = result.output
        self.command_history.append({"command": code, "success": result.success})
        self.db.log_command(self.student["id"], self.student["level"], code, result.success)

        if result.success:
            self.db.add_xp(self.student["id"], 10)
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (90, 255, 170), 18)
            self.student = self.db.get_or_create_student("Alex")
        else:
            self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (255, 100, 130), 12)

        self.input_text = ""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKQUOTE:
                    self.terminal_open = not self.terminal_open
                elif self.terminal_open:
                    if event.key == pygame.K_RETURN:
                        self.apply_code()
                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]
                    elif event.unicode and ord(event.unicode) >= 32:
                        self.input_text += event.unicode

    def update_player(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player.move_left()
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player.move_right()
        else:
            self.player.vx *= 0.75

        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.player.on_ground:
            self.player.jump()

        self.player.vy += 0.55
        self.player.rect.x += int(self.player.vx)
        self.player.rect.y += int(self.player.vy)

        self.player.on_ground = False
        for platform in self.platforms:
            if self.player.rect.colliderect(platform):
                if self.player.vy >= 0 and self.player.rect.bottom - self.player.vy <= platform.top + 12:
                    self.player.rect.bottom = platform.top
                    self.player.vy = 0
                    self.player.on_ground = True

        if self.player.rect.x < 0:
            self.player.rect.x = 0
        if self.player.rect.x > 920:
            self.player.rect.x = 920

        if self.player.rect.y > 640:
            self.player.rect.y = 420
            self.player.vy = 0

        if self.player.rect.colliderect(self.door.rect):
            if self.door.is_locked:
                self.player.rect.x -= 20
            else:
                self.spawn_particles(self.player.rect.centerx, self.player.rect.centery, (135, 220, 255), 16)

        if self.player.rect.colliderect(self.portal.rect) and self.door.is_locked is False:
            self.portal.active = False
            self.console_output = "Portal unlocked! Level complete."
            self.spawn_particles(self.portal.rect.centerx, self.portal.rect.centery, (255, 220, 90), 32)

    def draw_background(self):
        self.screen.fill((9, 12, 24))
        for i in range(0, 980, 120):
            pygame.draw.rect(self.screen, (18, 28, 42), (i - self.background_scroll % 120, 80, 80, 220))
        for i in range(0, 980, 160):
            pygame.draw.circle(self.screen, (55, 100, 200), (i - self.background_scroll % 160, 140 + (i % 3) * 25), 18)

    def draw_world(self):
        self.background_scroll += 1
        self.draw_background()

        for platform in self.platforms:
            pygame.draw.rect(self.screen, (34, 117, 109), platform)
            pygame.draw.rect(self.screen, (99, 214, 255), platform.inflate(-8, -6))

        door_color = (0, 220, 120) if not self.door.is_locked else (220, 60, 70)
        pygame.draw.rect(self.screen, door_color, self.door.rect)
        pygame.draw.rect(self.screen, (255, 255, 255), self.door.rect.inflate(-8, -8))

        pygame.draw.rect(self.screen, (90, 150, 255), self.player.rect)
        pygame.draw.rect(self.screen, (180, 230, 255), self.player.rect.inflate(-10, -8))

        portal_color = (255, 200, 90) if self.portal.active else (90, 90, 90)
        pygame.draw.ellipse(self.screen, portal_color, self.portal.rect)
        pygame.draw.ellipse(self.screen, (255, 245, 190), self.portal.rect.inflate(-12, -12))

        for particle in self.particles[:]:
            particle.update()
            particle.draw(self.screen)
            if particle.life <= 0:
                self.particles.remove(particle)

    def draw_terminal(self):
        if not self.terminal_open:
            return

        panel = pygame.Surface((930, 200), pygame.SRCALPHA)
        panel.fill((8, 14, 20, 215))
        self.screen.blit(panel, (25, 20))

        header = self.font_small.render("Neon Terminal // learning console", True, (135, 230, 255))
        self.screen.blit(header, (40, 30))

        prompt = self.font.render(f"> {self.input_text}_", True, (120, 255, 160))
        self.screen.blit(prompt, (40, 60))

        output = self.font.render(f"Output: {self.console_output[:120]}", True, (220, 220, 220))
        self.screen.blit(output, (40, 92))

        hint = self.font_small.render(
            "Examples: player.move_right(2) | door.unlock() | UPDATE doors SET is_locked = 0 | db.export_teacher_report()",
            True,
            (120, 120, 150),
        )
        self.screen.blit(hint, (40, 172))

    def run(self):
        while self.running:
            self.handle_events()
            self.update_player()
            self.draw_world()
            self.draw_terminal()

            hud = self.font.render(f"XP: {self.student['xp']}   Level: {self.student['level']}   Door: {'OPEN' if not self.door.is_locked else 'LOCKED'}", True, (245, 245, 245))
            self.screen.blit(hud, (25, 595))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
