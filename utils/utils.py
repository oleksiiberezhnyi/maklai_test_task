from bs4 import BeautifulSoup
import re
import aiohttp
from db.models import Post, ReleaseLink, PepLink, Files
from db.models import session


async def parse_articles(data):
    articles = data.find_all("div", "date-outer")
    for article in articles:
        try:
            date = article.h2.get_text()
        except AttributeError:
            date = ""
        try:
            title = article.find("h3").get_text().replace("\n", "")
        except AttributeError:
            title = ""
        try:
            text = article.find(class_="post-body").get_text()
        except AttributeError:
            text = ""
        try:
            author = article.find(class_="fn").get_text()
        except AttributeError:
            author = ""
        post_obj = save_post(date, title, text, author)
        try:
            release_link = article.find("a", href=re.compile("^https://www.python.org/downloads/release/python-"))["href"]
            await parse_release_link(release_link, post_obj)
        except (AttributeError, TypeError):
            release_link = ""


async def parse_release_link(link, post: Post):
    if link is not None:
        async with aiohttp.ClientSession() as session:
            async with session.get(link, ssl=False) as r:
                page_content = await r.text()
                page_soup = BeautifulSoup(page_content, "html.parser")
                get_data_from_release(page_soup, post)


def get_data_from_release(data: BeautifulSoup, post: Post):
    files_table = data.table.extract()
    try:
        title = data.title.get_text()
    except AttributeError:
        title = ""
    try:
        h1 = data.article.h1.get_text()
    except AttributeError:
        h1 = ""
    try:
        date = data.find(text="Release Date:").find_parent("p").get_text().replace("Release Date: ", "")
    except AttributeError:
        date = ""
    try:
        text = data.article.get_text()
    except AttributeError:
        text = ""
    pep_links = data.find_all("a", href=re.compile("^https://www.python.org/dev/peps/pep-"))
    release_obj = save_release_link(title, h1, date, text, post)
    save_pep_links(pep_links, release_obj)
    parse_files(files_table, release_obj)


def parse_files(table, release: ReleaseLink):
    trs = table.tbody.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        version_link = tds[0].a["href"]
        operation_system = tds[1].get_text()
        description = tds[2].get_text()
        md5_sum = tds[3].get_text()
        file_size = tds[4].get_text()
        gpg_link = tds[5].a["href"]
        save_file(version_link, operation_system, description, md5_sum, file_size, gpg_link, release)


def save_post(date, title, text, author):
    post = Post(
        date=date,
        title=title,
        text=text,
        author=author
    )
    session.add(post)
    session.commit()
    return post


def save_release_link(title, h1, date, text, post: Post):
    release_link = ReleaseLink(
        title=title,
        h1=h1,
        date=date,
        text=text,
        post_id=post.id
    )
    session.add(release_link)
    session.commit()
    return release_link


def save_pep_links(links, release: ReleaseLink):
    if links:
        for link in links:
            pep_link = PepLink(
                link=link["href"],
                release_link_id=release.id
            )
            session.add(pep_link)
        session.commit()
    return


def save_file(version_link, operation_system, description, md5_sum, file_size, gpg_link, release: ReleaseLink):
    file = Files(
        version_link=version_link,
        operation_system=operation_system,
        description=description,
        md5_sum=md5_sum,
        file_size=int(file_size),
        gpg_link=gpg_link,
        release_link_id=release.id
    )
    session.add(file)
    session.commit()
    return
