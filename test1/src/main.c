#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"

// 定义 LED 的 GPIO
#define LED1_GPIO  GPIO_NUM_36
#define LED2_GPIO  GPIO_NUM_35

// 定义流水灯速度（毫秒）
#define DELAY_MS   500

// 将要使用的 GPIO 放入一个数组，便于循环操作
const gpio_num_t led_gpios[] = {LED1_GPIO, LED2_GPIO};
const int led_count = sizeof(led_gpios) / sizeof(led_gpios[0]);

void app_main(void)
{
    // 1. GPIO 配置结构体
    gpio_config_t io_conf = {};
    
    // 2. 设置这些 GPIO 为输出模式
    io_conf.mode = GPIO_MODE_OUTPUT;
    
    // 3. 禁用上拉/下拉
    io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
    io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
    
    // 4. 配置 GPIO 的位掩码（Bit Mask）
    // 我们需要为每个要设置的 GPIO 创建一个位掩码
    io_conf.pin_bit_mask = 0;
    for (int i = 0; i < led_count; i++) {
        io_conf.pin_bit_mask |= (1ULL << led_gpios[i]);
    }
    
    // 5. 根据以上设置配置 GPIO
    gpio_config(&io_conf);
    
    // 初始化时关闭所有 LED
    for (int i = 0; i < led_count; i++) {
        gpio_set_level(led_gpios[i], 0);
    }
    
    // 主循环
    while (1) {
        // 流水灯效果：逐个点亮，再逐个熄灭
        for (int i = 0; i < led_count; i++) {
            gpio_set_level(led_gpios[i], 1); // 点亮当前 LED
            vTaskDelay(DELAY_MS / portTICK_PERIOD_MS); // 等待
            gpio_set_level(led_gpios[i], 0); // 熄灭当前 LED
        }
        
        // 另一种效果：依次点亮然后依次熄灭（追逐效果）
        /*
        for (int i = 0; i < led_count; i++) {
            gpio_set_level(led_gpios[i], 1); // 点亮
            vTaskDelay(DELAY_MS / portTICK_PERIOD_MS);
        }
        for (int i = 0; i < led_count; i++) {
            gpio_set_level(led_gpios[i], 0); // 熄灭
            vTaskDelay(DELAY_MS / portTICK_PERIOD_MS);
        }
        */
    }
}