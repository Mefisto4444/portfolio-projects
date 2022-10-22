import requests, bs4, csv, re
from sys import exit, argv

if len(argv) == 2:
    res = requests.get(str(argv[1]))
res = requests.get('https://www.amazon.pl/gp/bestsellers/books/20788963031/ref=zg_bs_nav_books_2_20788968031')
try:
    res.raise_for_status()
except Exception as Ex:
    print('Exception',Ex)
    exit()

def extract_data(html_code, parser = 'html.parser'):
    while True:
        amazon_soup = bs4.BeautifulSoup(html_code, parser)
        books = amazon_soup.select("#gridItemRoot")
        for book in books:
            try:
                link = f'https://www.amazon.pl{book.select(".a-link-normal")[0].get("href")}'
                tittle = book.select(".a-link-normal")[1].select("div")[0].text
                author = book.select("div[class='a-row a-size-small']")[0].text
                cover = book.select("div[class='a-row a-size-small']")[1].select("span")[0].text
                opinion = book.select("div.a-row")[1].select("span")[0].text.replace(" ","").strip('gwiazdek').replace("z","/")
                opinions = book.select("div.a-row")[1].select("span")[-1].text + " opinions"
                price = book.select("div.a-row")[-1].select("span")[-1].text
            except IndexError:
                continue
            yield [tittle, author, price, opinion, opinions, cover, link]
        try:
            next = amazon_soup.select("li.a-last")[0].select("a")[0].get('href')
            html_code = requests.get("https://www.amazon.pl/" + next).text
        except IndexError:
            return None
data_file = open('amazon_books_data.csv','w',newline='')
data_file_writer = csv.writer(data_file,delimiter=";")
for book_info in extract_data(res.text):
    print(book_info,end="\n\n")
    data_file_writer.writerow(book_info)
data_file.close()
    #'https://www.amazon.pl/gp/bestsellers/books/20788968031?ref_=Oct_d_obs_S&pd_rd_w=sJaE2&content-id=amzn1.sym.f3c0087e-c101-4b01-8657-8ee971af1154&pf_rd_p=f3c0087e-c101-4b01-8657-8ee971af1154&pf_rd_r=91BWZG0THY81K0SE07KG&pd_rd_wg=wwvyK&pd_rd_r=7bea8f14-2914-4dbf-8642-a21c57d39a86'
