import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit
import os
from pathvalidate import sanitize_filename
import argparse


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(book_id, url, filename, folder='books/'):
    params = {'id' : book_id}
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    filepath = os.path.join(f'{folder}{sanitize_filename(filename)}.txt')
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(full_book_img_url, folder='images/'):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(full_book_img_url)
    response.raise_for_status()
    check_for_redirect(response)
    image_name = urlsplit(full_book_img_url).path.split('/')[-1]
    filepath = os.path.join(folder, image_name)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def parse_book_page(response, url):
    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('h1').text
    title, author = title_tag.split('::')
    book_img_url = soup.find('div', class_='bookimage').find('img')['src']
    full_book_img_url = urljoin(url, book_img_url)
    comments = soup.find_all('div', class_='texts')
    book_comments = [comment.find(
        'span', class_='black').text for comment in comments]
    genres = soup.find('span', class_='d_book').find_all('a')
    book_genre = [genre.text for genre in genres]
    book_parametrs = {'title': title_tag,
                      'img_url': full_book_img_url,
                      'genre': book_genre,
                      'comments': book_comments,
                      'author': author}
    return book_parametrs


def main():
    parser = argparse.ArgumentParser(
        description='Программа помогает скачивать изображение, текст и информацию о книгах.')
    parser.add_argument('--start_id', type=int,
                        help='Введите айди начала книги',
                        default=1)
    parser.add_argument('--end_id', type=int,
                        help='Введите айди конечной книги',
                        default=10)
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            url = f'https://tululu.org/b{book_id}/'
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            book_parameters = parse_book_page(response, url)
            url = 'https://tululu.org/txt.php'
            download_txt(book_id, url, book_parameters['title'].strip())
            download_image(book_parameters['img_url'])
        except requests.exceptions.HTTPError:
            print("книга не найдена")


if __name__ == '__main__':
    main()
