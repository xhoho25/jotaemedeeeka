# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

from requests import get as rget, head as rhead, post as rpost, Session as rsession
from re import findall as re_findall, sub as re_sub, match as re_match, search as re_search
from urllib.parse import urlparse, unquote
from json import loads as jsonloads
from lk21 import Bypass
from cfscrape import create_scraper
from bs4 import BeautifulSoup
from lxml.etree import HTML as etree_html
from base64 import standard_b64encode, b64decode
from time import sleep

from bot import LOGGER, UPTOBOX_TOKEN, SHARER_EMAIL, SHARER_PASS, GDTOT_CRYPT
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException

fmed_list = ['fembed.net', 'fembed.com', 'femax20.com', 'fcdn.stream', 'feurl.com', 'layarkacaxxi.icu',
             'naniplay.nanime.in', 'naniplay.nanime.biz', 'naniplay.com', 'mm9842.com']


def direct_link_generator(link: str):
    """ direct links generator """
    try:
        domain = urlparse(link).netloc
    except:
        raise DirectDownloadLinkException("ERROR: Invalid URL")
    if 'youtube.com' in domain or 'youtu.be' in domain:
        raise DirectDownloadLinkException("ERROR: Use ytdl cmds for Youtube links")
    elif 'yadi.sk' in domain or 'disk.yandex.com' in domain:
        return yandex_disk(link)
    elif 'mediafire.com' in domain:
        return mediafire(link)
    elif 'uptobox.com' in domain:
        return uptobox(link)
    elif 'osdn.net' in domain:
        return osdn(link)
    elif 'github.com' in domain:
        return github(link)
    elif 'hxfile.co' in domain:
        return hxfile(link)
    elif 'anonfiles.com' in domain:
        return anonfiles(link)
    elif 'letsupload.io' in domain:
        return letsupload(link)
    elif '1drv.ms' in domain:
        return onedrive(link)
    elif 'pixeldrain.com' in domain:
        return pixeldrain(link)
    elif 'antfiles.com' in domain:
        return antfiles(link)
    elif 'streamtape.com' in domain:
        return streamtape(link)
    elif 'bayfiles.com' in domain:
        return anonfiles(link)
    elif 'racaty.net' in domain:
        return racaty(link)
    elif '1fichier.com' in domain:
        return fichier(link)
    elif 'solidfiles.com' in domain:
        return solidfiles(link)
    elif 'krakenfiles.com' in domain:
        return krakenfiles(link)
    elif 'upload.ee' in domain:
        return uploadee(link)
    elif any(x in domain for x in ['appdrive', 'driveapp']):
        return drive_sharer(link)
    elif 'gdtot' in domain:
        return gdtot(link)
    elif 'hubdrive' in domain:
        return hubdrive(link)
    elif any(x in domain for x in fmed_list):
        return fembed(link)
    elif any(x in domain for x in ['sbembed.com', 'watchsb.com', 'streamsb.net', 'sbplay.org']):
        return sbembed(link)
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')

def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct """
    try:
        link = re_findall(r'\b(https?://(yadi.sk|disk.yandex.com)\S+)', url)[0][0]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        return rget(api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException("ERROR: File not found/Download limit reached")

def uptobox(url: str) -> str:
    """ Uptobox direct link generator
    based on https://github.com/jovanzers/WinTenCermin and https://github.com/sinoobie/noobie-mirror """
    try:
        link = re_findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Uptobox links found")
    if UPTOBOX_TOKEN is None:
        LOGGER.error('UPTOBOX_TOKEN not provided!')
        dl_url = link
    else:
        try:
            link = re_findall(r'\bhttps?://.*\.uptobox\.com/dl\S+', url)[0]
            dl_url = link
        except:
            file_id = re_findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
            file_link = f'https://uptobox.com/api/link?token={UPTOBOX_TOKEN}&file_code={file_id}'
            try:
                req = rget(file_link)
            except Exception as e:
                raise DirectDownloadLinkException(f"ERROR: {e}")
            result = req.json()
            if result['message'].lower() == 'success':
                dl_url = result['data']['dlLink']
            elif result['message'].lower() == 'waiting needed':
                waiting_time = result["data"]["waiting"] + 1
                waiting_token = result["data"]["waitingToken"]
                sleep(waiting_time)
                req2 = rget(f"{file_link}&waitingToken={waiting_token}")
                result2 = req2.json()
                dl_url = result2['data']['dlLink']
            elif result['message'].lower() == 'you need to wait before requesting a new download link':
                cooldown = divmod(result['data']['waiting'], 60)
                raise DirectDownloadLinkException(f"ERROR: Uptobox is being limited please wait {cooldown[0]} min {cooldown[1]} sec.")
            else:
                LOGGER.info(f"UPTOBOX_ERROR: {result}")
                raise DirectDownloadLinkException(f"ERROR: {result['message']}")
    return dl_url

def mediafire(url: str) -> str:
    """ MediaFire direct link generator """
    try:
        link = re_findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found")
    try:
        page = BeautifulSoup(rget(link).content, 'lxml')
        info = page.find('a', {'aria-label': 'Download file'})
        return info.get('href')
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def osdn(url: str) -> str:
    """ OSDN direct link generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re_findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No OSDN links found")
    try:
        page = BeautifulSoup(rget(link, allow_redirects=True).content, 'lxml')
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    info = page.find('a', {'class': 'mirror_link'})
    link = unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re_sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]

def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re_findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No GitHub Releases links found")
    download = rget(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("ERROR: Can't extract the link")

def hxfile(url: str) -> str:
    """ Hxfile direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        return Bypass().bypass_filesIm(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def anonfiles(url: str) -> str:
    """ Anonfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        return Bypass().bypass_anonfiles(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def letsupload(url: str) -> str:
    """ Letsupload direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        link = re_findall(r'\bhttps?://.*letsupload\.io\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Letsupload links found\n")
    try:
        return Bypass().bypass_url(link)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def fembed(link: str) -> str:
    """ Fembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        dl_url= Bypass().bypass_fembed(link)
        count = len(dl_url)
        lst_link = [dl_url[i] for i in dl_url]
        return lst_link[count-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def sbembed(link: str) -> str:
    """ Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        dl_url= Bypass().bypass_sbembed(link)
        count = len(dl_url)
        lst_link = [dl_url[i] for i in dl_url]
        return lst_link[count-1]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def onedrive(link: str) -> str:
    """ Onedrive direct link generator
    Based on https://github.com/UsergeTeam/Userge """
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8")
    direct_link1 = f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    try:
        resp = rhead(direct_link1)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    if resp.status_code != 302:
        raise DirectDownloadLinkException("ERROR: Unauthorized link, the link may be private")
    return resp.next.url

def pixeldrain(url: str) -> str:
    """ Based on https://github.com/yash-dk/TorToolkit-Telegram """
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"https://pixeldrain.com/api/list/{file_id}/zip"
    else:
        info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
        dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    try:
        resp = rget(info_link).json()
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException(f"ERROR: Cant't download due {resp['message']}.")

def antfiles(url: str) -> str:
    """ Antfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        return Bypass().bypass_antfiles(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def streamtape(url: str) -> str:
    """ Streamtape direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        return Bypass().bypass_streamtape(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def racaty(url: str) -> str:
    """ Racaty direct link generator
    based on https://github.com/SlamDevs/slam-mirrorbot"""
    dl_url = ''
    try:
        re_findall(r'\bhttps?://.*racaty\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Racaty links found")
    try:
        scraper = create_scraper()
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        op = soup.find("input", {"name": "op"})["value"]
        ids = soup.find("input", {"name": "id"})["value"]
        rapost = scraper.post(url, data = {"op": op, "id": ids})
        rsoup = BeautifulSoup(rapost.text, "lxml")
        dl_url = rsoup.find("a", {"id": "uniqueExpirylink"})["href"].replace(" ", "%20")
        return dl_url
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def fichier(link: str) -> str:
    """ 1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = re_match(regex, link)
    if not gan:
      raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
      pswd = link.split("::")[-1]
      url = link.split("::")[-2]
    else:
      pswd = None
      url = link
    try:
      if pswd is None:
        req = rpost(url)
      else:
        pw = {"pass": pswd}
        req = rpost(url, data=pw)
    except:
      raise DirectDownloadLinkException("ERROR: Unable to reach 1fichier server!")
    if req.status_code == 404:
      raise DirectDownloadLinkException("ERROR: File not found/The link you entered is wrong!")
    soup = BeautifulSoup(req.content, 'lxml')
    if soup.find("a", {"class": "ok btn-general btn-orange"}) is not None:
        dl_url = soup.find("a", {"class": "ok btn-general btn-orange"})["href"]
        if dl_url is None:
          raise DirectDownloadLinkException("ERROR: Unable to generate Direct Link 1fichier!")
        else:
          return dl_url
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
        str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_2).lower():
            numbers = [int(word) for word in str(str_2).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException("ERROR: 1fichier is on a limit. Please wait a few minutes/hour.")
            else:
                raise DirectDownloadLinkException(f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.")
        elif "protect access" in str(str_2).lower():
          raise DirectDownloadLinkException(f"ERROR: This link requires a password!\n\n<b>This link requires a password!</b>\n- Insert sign <b>::</b> after the link and write the password after the sign.\n\n<b>Example:</b> https://1fichier.com/?smmtd8twfpm66awbqz04::love you\n\n* No spaces between the signs <b>::</b>\n* For the password, you can use a space!")
        else:
            raise DirectDownloadLinkException("ERROR: Failed to generate Direct Link from 1fichier!")
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 4:
        str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
        str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_1).lower():
            numbers = [int(word) for word in str(str_1).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException("ERROR: 1fichier is on a limit. Please wait a few minutes/hour.")
            else:
                raise DirectDownloadLinkException(f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.")
        elif "bad password" in str(str_3).lower():
          raise DirectDownloadLinkException("ERROR: The password you entered is wrong!")
        else:
            raise DirectDownloadLinkException("ERROR: Error trying to generate Direct Link from 1fichier!")
    else:
        raise DirectDownloadLinkException("ERROR: Error trying to generate Direct Link from 1fichier!")

def solidfiles(url: str) -> str:
    """ Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18 """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        pageSource = rget(url, headers = headers).text
        mainOptions = str(re_search(r'viewerOptions\'\,\ (.*?)\)\;', pageSource).group(1))
        return jsonloads(mainOptions)["downloadUrl"]
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def krakenfiles(page_link: str) -> str:
    """ krakenfiles direct link generator
    Based on https://github.com/tha23rd/py-kraken
    By https://github.com/junedkh """
    client = rsession()
    try:
        page_resp = client.get(page_link)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    soup = BeautifulSoup(page_resp.text, "lxml")
    try:
        token = soup.find("input", id="dl-token")["value"]
    except:
        raise DirectDownloadLinkException(f"ERROR: Page link is wrong: {page_link}")
    hashes = [
        item["data-file-hash"]
        for item in soup.find_all("div", attrs={"data-file-hash": True})
    ]
    if not hashes:
        raise DirectDownloadLinkException(f"ERROR: Hash not found for : {page_link}")
    dl_hash = hashes[0]
    payload = f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="token"\r\n\r\n{token}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "cache-control": "no-cache",
        "hash": dl_hash,
    }
    dl_link_resp = client.post(f"https://krakenfiles.com/download/{hash}", data=payload, headers=headers)
    dl_link_json = dl_link_resp.json()
    if "url" in dl_link_json:
        return dl_link_json["url"]
    else:
        raise DirectDownloadLinkException(f"ERROR: Failed to acquire download URL from kraken for : {page_link}")

def uploadee(url: str) -> str:
    """ uploadee direct link generator
    By https://github.com/iron-heart-x"""
    try:
        soup = BeautifulSoup(rget(url).content, 'lxml')
        sa = soup.find('a', attrs={'id':'d_l'})
        return sa['href']
    except:
        raise DirectDownloadLinkException(f"ERROR: Failed to acquire download URL from upload.ee for : {url}")

def drive_sharer(url: str) -> str:
    """ Appdrive google drive link generator
        By https://github.com/xcscxr """
    if not SHARER_EMAIL:
        raise DirectDownloadLinkException("ERROR: SHARER_EMAIL not provided")
    temp = urlparse(url)
    client = rsession()
    try:
        client.headers.update(
            {"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"})
        client.post(f'{temp.scheme}://{temp.netloc}/login', data={'email': SHARER_EMAIL, 'password': SHARER_PASS})
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    try:
        client.cookies.get_dict()['MD']
    except:
        raise DirectDownloadLinkException("ERROR: invalid SHARER EMAIL and PASSWORD provided")
    try:
        res = client.get(url)
        key = re_findall('"key",\s+"(.*?)"', res.text)[0]
        ddl_btn = etree_html(res.content).xpath("//button[@id='drc']")
        data = {'type': 1, 'key': key, 'action': 'original'}
        info = re_findall(r'>(.*?)<\/li>', res.text)
        info_parsed = {}
        for item in info:
            kv = [s.strip() for s in item.split(':', maxsplit=1)]
            info_parsed[kv[0].lower()] = kv[1]
        info_parsed['error'] = False
        info_parsed['link_type'] = 'login'
        if ddl_btn:
            info_parsed['link_type'] = 'direct'
            data['action'] = 'direct'
        while data['type'] <= 3:
            try:
                data_string = ''
                for item in data:
                    data_string += f'------_\r\n'
                    data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
                data_string += f'------_--\r\n'
                resp = client.post(url, data=data_string, headers={"Content-Type": "multipart/form-data; boundary=----_"}).json()
                break
            except:
                data['type'] += 1
        drive_link = None
        if 'url' in resp:
            drive_link = resp['url']
        elif 'error' in resp:
            info_parsed["error"] = True
        if drive_link and not info_parsed['error'] and 'driveapp' in temp.netloc:
            res = client.get(drive_link)
            drive_link = etree_html(res.content).xpath("//a[contains(@class,'btn')]/@href")[0]
        client.get(f'{temp.scheme}://{temp.netloc}/logout')
        if drive_link:
            return drive_link
        raise DirectDownloadLinkException(resp['message'])
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")

def gdtot(url: str) -> str:
    """ Gdtot google drive link generator
    By https://github.com/xcscxr """
    if not GDTOT_CRYPT:
        raise DirectDownloadLinkException("ERROR: GDTOT_CRYPT not provided")
    parsed_url = urlparse(url)
    client = rsession()
    try:
        client.cookies.set(name='crypt', value=GDTOT_CRYPT, domain=parsed_url.netloc)
        res = client.get(url)
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    try:
        res = client.get(f"{parsed_url.scheme}://{parsed_url.netloc}/dld?id={url.split('/')[-1]}")
        matches = re_findall('gd=(.*?)&', res.text)
        decoded_id = b64decode(str(matches[0])).decode('utf-8')
        return f'https://drive.google.com/open?id={decoded_id}'
    except:
        raise DirectDownloadLinkException("ERROR: Try in your browser, mostly file not found or user limit exceeded!")

def hubdrive(url: str) -> str:
    """ Hubdrive google drive link generator
    By https://github.com/xcscxr """
    if not SHARER_EMAIL:
        raise DirectDownloadLinkException("ERROR: SHARER_EMAIL not provided")
    parsed_url = urlparse(url)
    client = rsession()
    try:
        client.post(f'{parsed_url.scheme}://{parsed_url.netloc}/sign', data={'email': SHARER_EMAIL, 'pass': SHARER_PASS})
    except Exception as e:
        raise DirectDownloadLinkException(f"ERROR: {e}")
    try:
        client.cookies.get_dict()['crypt']
    except:
        raise DirectDownloadLinkException("ERROR: invalid SHARER_EMAIL")
    try:
        res = client.get(url)
        req_url = f"{parsed_url.scheme}://{parsed_url.netloc}/ajax.php?ajax=download"
        res = client.post(req_url, headers={'x-requested-with': 'XMLHttpRequest'}, data={'id': url.split('/')[-1]}).json()['file']
        client.get(f'{parsed_url.scheme}://{parsed_url.netloc}/login.php?action=logout')
        return f'https://drive.google.com/open?id={res.split("gd=")[-1]}'
    except:
        raise DirectDownloadLinkException("ERROR: Try in your browser, mostly file not found or user limit exceeded!")