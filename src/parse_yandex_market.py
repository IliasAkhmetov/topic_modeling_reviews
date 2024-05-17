from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import re
import time
import random
import csv

# Парсинг отзывов с 1 по 100 странице сортированные по полезности, позитивные, негативные, нейтральные

class WebScrap_and_save:
    def __init__(self, url, start_page, end_page, specific_name):
        self.url = url
        self.start_page = start_page
        self.end_page = end_page
        self.specific_name = specific_name
    def save_to_csv(self, batch_data, filename, mode='a'):
        keys = batch_data[0].keys()
        with open(filename, mode, newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            if output_file.tell() == 0:  # Если файл пустой, пишем заголовки
                dict_writer.writeheader()
            dict_writer.writerows(batch_data)
    def parsing_yandex_market(self):
        base_url = self.url
        driver = webdriver.Chrome()
        time.sleep(random.uniform(1.5, 3.5))
        batch_size = 50  # Размер пачки для сохранения
        batch_data = []  # Список для временного хранения данных пачки
        for i in range(self.start_page, self.end_page + 1):
            try:
                url = base_url + str(i)
                driver.get(url)
                time.sleep(random.uniform(1.5, 3.5))
                # Получаем отзывы
                reviews = driver.find_elements(By.CSS_SELECTOR, '[data-zone-name="product-review"]')
                for review in reviews:
                    # Авторы
                    # author_web_element = review.find_element(By.CSS_SELECTOR, '._1UL8e._1mJcZ')
                    # author = author_web_element.text

                    # Получаем дату и город (Изменить потом для даты и города)
                    try:
                        date_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="date_region"]')
                        date_city = date_web_element.text
                        # Отделяем дату и город
                        date, city = date_city.split(', ')
                    except NoSuchElementException:
                        date, city = 'Не указано', 'Не указано'

                    # Получаем оценку
                    score_web_element = review.find_element(By.CSS_SELECTOR, "div[data-rate]")
                    rating = score_web_element.get_attribute('data-rate')

                    # Опыт использования
                    try:
                        review_usage_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="review-usage"]')
                        review_usage = review_usage_web_element.text.replace('Опыт использования: ', '')
                    except NoSuchElementException:
                        review_usage = 'Не указано'

                    # Достинства
                    try:
                        review_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="review-pro"]')
                        review_pro = re.sub(r'\n*Достоинства:\s*', '', review_web_element.text)
                    except NoSuchElementException:
                        review_pro = 'Не указано'

                    # Недостатки
                    try:
                        review_contra_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="review-contra"]')
                        review_contra = re.sub(r'\n*Недостатки:\s*', '', review_contra_web_element.text)
                    except NoSuchElementException:
                        review_contra = 'Не указано'

                    # Комментарии
                    try:
                        review_comment_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="review-comment"]')
                        review_comment = re.sub(r'\n*Комментарий:\s*', '', review_comment_web_element.text)
                    except NoSuchElementException:
                        review_comment = 'Не указано'

                    # Количество лайкнувших отзыв
                    like_button = review.find_element(By.CSS_SELECTOR, '[data-auto="review-like"]')
                    like_count_web_element = like_button.find_element(By.CSS_SELECTOR, '[data-auto="count"]')
                    like_count = like_count_web_element.text

                    # Количество дизлайкнувших отзыв
                    dislike_button = review.find_element(By.CSS_SELECTOR, '[data-auto="review-dislike"]')
                    dislike_count_web_element = dislike_button.find_element(By.CSS_SELECTOR, '[data-auto="count"]')
                    dislike_count = dislike_count_web_element.text

                    # Магазин, где был куплен
                    review_shop_web_element = review.find_element(By.CSS_SELECTOR, '[data-auto="review-shop-name"]')
                    shop_review = review_shop_web_element.text.replace('Товар продавца ',
                                                                       '') if review_shop_web_element.text else 'Неизвестно'

                    time.sleep(random.uniform(0.5, 2.0))
                    # Создаем словарь хранения
                    inf_dict = {
                        'Date': date,
                        'City': city,
                        'Score': rating,
                        'Review_usage': review_usage,
                        'Review_pro': review_pro,
                        'Review_contra': review_contra,
                        'Review_comment': review_comment,
                        'Like_count': like_count,
                        'Dislike_counts': dislike_count,
                        'Shop_review': shop_review
                    }
                    # Добавляем словарь в пачку
                    batch_data.append(inf_dict)
                    if len(batch_data) >= batch_size:
                        self.save_to_csv(batch_data, f'../data/{self.specific_name}_reviews.csv')
                        batch_data = []  # Очищаем пачку после сохранения
            except Exception as e:
                print(f'Произошла ошибка: {e}')
                break  # Прерываем цикл при возникновении ошибки
            # Не забыть сохранить оставшиеся данные после завершения цикла
        if batch_data:
            self.save_to_csv(batch_data, f'../data/{self.specific_name}_reviews.csv')
        driver.quit()

url = 'https://market.yandex.ru/product--iphone-14/1768753750/reviews?sku=101960159735&uniqueId=117959627&do-waremd5=gThrjSWcXjyM0WmPYL-9pQ&grade_value=3&grade_value=4&page='
start_page = 1
end_page = 26
specific_name = 'neutral'
reviews_data = WebScrap_and_save(url, start_page, end_page, specific_name)
reviews_data.parsing_yandex_market()
