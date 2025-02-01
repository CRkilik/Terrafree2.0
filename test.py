import arcade

# Константы для размеров окна
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Простой кликер"

# Константы для кнопки
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 100
BUTTON_X = SCREEN_WIDTH // 2
BUTTON_Y = SCREEN_HEIGHT // 2

class ClickerGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.score = 0  # Счетчик очков
        self.button_pressed = False  # Флаг нажатия кнопки

    def on_draw(self):
        """Отрисовка всех элементов."""
        self.clear()  # Очищаем экран (замена start_render())
        
        # Отрисовка фона
        arcade.set_background_color(arcade.color.WHITE)
        
        # Отрисовка кнопки
        if self.button_pressed:
            arcade.draw_lrbt_rectangle_filled(
                BUTTON_X - BUTTON_WIDTH / 2,  # left
                BUTTON_X + BUTTON_WIDTH / 2,  # right
                BUTTON_Y - BUTTON_HEIGHT / 2, # bottom
                BUTTON_Y + BUTTON_HEIGHT / 2, # top
                arcade.color.GREEN
            )
        else:
            arcade.draw_lrbt_rectangle_filled(
                BUTTON_X - BUTTON_WIDTH / 2,
                BUTTON_X + BUTTON_WIDTH / 2,
                BUTTON_Y - BUTTON_HEIGHT / 2,
                BUTTON_Y + BUTTON_HEIGHT / 2,
                arcade.color.BLUE
            )
        
        # Текст на кнопке
        arcade.draw_text("Кликни меня!", 
                         BUTTON_X - 70, BUTTON_Y - 10, 
                         arcade.color.WHITE, 18)
        
        # Отрисовка счетчика очков
        arcade.draw_text(f"Очки: {self.score}", 
                         10, SCREEN_HEIGHT - 30, 
                         arcade.color.BLACK, 24)

    def on_mouse_press(self, x, y, button, modifiers):
        """Обработка нажатия мыши."""
        # Проверка, находится ли курсор внутри кнопки
        if (BUTTON_X - BUTTON_WIDTH / 2 < x < BUTTON_X + BUTTON_WIDTH / 2 and
            BUTTON_Y - BUTTON_HEIGHT / 2 < y < BUTTON_Y + BUTTON_HEIGHT / 2):
            self.button_pressed = True
            self.score += 1  # Увеличиваем счетчик очков

    def on_mouse_release(self, x, y, button, modifiers):
        """Обработка отпускания кнопки мыши."""
        self.button_pressed = False

def main():
    """Главная функция."""
    game = ClickerGame()
    arcade.run()

if __name__ == "__main__":
    main()
