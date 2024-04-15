import requests
import undetected_chromedriver as uc
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import multiprocessing
import shutil # to save it locally
import PIL
import datetime
from PIL import Image
from selenium.webdriver.support.ui import WebDriverWait
import sqlalchemy as db
import numpy as np
import os
from slugify import slugify
import traceback
import threading
from selenium.webdriver.support import expected_conditions as EC
import paramiko
import requests
from sqlalchemy import and_ ,text,select,join,MetaData
def website_tables(engine, metadata, wp):
       posts = db.Table(str(wp)+'_posts', metadata, autoload=True, autoload_with=engine)
       terms = db.Table(str(wp)+'_terms', metadata, autoload=True, autoload_with=engine)
       taxo = db.Table(str(wp)+'_term_taxonomy', metadata, autoload=True, autoload_with=engine)
       postmeta = db.Table(str(wp)+'_postmeta', metadata, autoload=True, autoload_with=engine)
       term_rela = db.Table(str(wp)+'_term_relationships', metadata, autoload=True, autoload_with=engine)
       term_meta = db.Table(str(wp)+'_termmeta', metadata, autoload=True, autoload_with=engine)
       return posts,terms,taxo,postmeta,term_rela,term_meta
def connectToWebsite(**kwargs):
        user=kwargs['user_db']
        db_mdp=kwargs['db_mdp']
        ip=kwargs['ip']
        name_db=kwargs['name_db']
        ftp_passe=kwargs['ftp_passe']
        engine = db.create_engine(
            'mysql+pymysql://' + str(user) + ':' + str(db_mdp) + '@' + str(ip) + '/' + str(name_db))
        metadata = db.MetaData()
        transport = paramiko.Transport((ip, 22))
        transport.connect(username='root', password=ftp_passe)
        sftp = paramiko.SFTPClient.from_transport(transport)        
        # Establish SSH connection with private key
        return engine, metadata,sftp

# Create a lock to ensure only one thread creates the directory
dir_creation_lock = threading.Lock()     
def download_page_img(*args):
  try:  
    chapitre_path='replace with local path'
    chap_num=args[2]
    pagenum=args[1]
    img_url=args[0]
    manga_path=args[3]
    direct=os.path.join(chapitre_path,manga_path,str(chap_num))
    # Use the lock to ensure only one thread creates the directory
    with dir_creation_lock:
        if not os.path.exists(direct) and not os.path.isdir(direct):
                print("Creating directory:", direct)
                os.mkdir(direct)

    filename=os.path.join(chapitre_path,manga_path,str(chap_num),str(pagenum)+'.jpg')
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "replace with website referer"  # Replace with the referring website URL
    }
    response = requests.get(img_url, headers=headers, stream=True, allow_redirects=True)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print("Image downloaded successfully!")
    else:
        print("Failed to download image.")
  except Exception as e : 
        print(f"Error downloading page {pagenum} for chapter {chap_num}: {str(e)}")
        traceback.print_exc()  # Print the traceback to help debug the issue

        
def find_page_chapitre(filename,search_path):
        result=[]
        for root, dir, files in os.walk(search_path):
            print(files)

            if filename in files:
                result.append(os.path.join(root, filename))
                print('ok')
        return result

        print(find_files("smpl.htm", "D:"))

        
def CheckCap(metadata,engine,wp,chapitre_title):
     
     posts = db.Table(str(wp)+'_posts', metadata, mysql_autoload=True, autoload_with=engine)
     with engine.begin() as connection:
        result=select(posts.c.ID).where(posts.c.post_title == chapitre_title)
        result_proxy = connection.execute(result) 
        rows = result_proxy.fetchall()
        print(rows)
        cat_id= [row[1] for row in rows]
        print(cat_id[1])
     if cat_id:
          return True
     else:
          return False
    

                   
def addAllChapteronDB(*args):
    #get content of each chapter
   
     chap_num=args[0]
     content=args[1]
     manga_title=args[2]
     chap_title=args[3]
     engine=args[4]
     metadata=args[5]
     sftp=args[6]
     
     posts = db.Table(str(wp)+'_posts', metadata, mysql_autoload=True, autoload_with=engine)
     terms = db.Table(str(wp)+'_terms', metadata, mysql_autoload=True, autoload_with=engine)
     taxo = db.Table(str(wp)+'_term_taxonomy', metadata, mysql_autoload=True, autoload_with=engine)
     postmeta = db.Table(str(wp)+'_postmeta', metadata, mysql_autoload=True, autoload_with=engine)
     term_rela = db.Table(str(wp)+'_term_relationships', metadata, mysql_autoload=True, autoload_with=engine)
     term_meta = db.Table(str(wp)+'_termmeta', metadata, mysql_autoload=True, autoload_with=engine)
    
     x = datetime.datetime.now()
     with engine.begin() as connection:
                
                print(chapitre_title)
                chapExist=False
                if not chapExist:
                    rey = posts.select().order_by(posts.columns.ID.desc()).limit(1)
                    sanaa = connection.execute(rey).fetchall()
                    last_id = sanaa[0][0]
                    guid_id=last_id+1
                    print(f' guid {sanaa}')
                    guid = site + '?post_type=blog&#038;p=' + str(guid_id)
                    chapitre_title=manga_name+' '+chap_num+' VF'
                    chapitre_slug=slugify(chapitre_title)
                    connection.execute(posts.insert(), {"post_author":'1', "post_date":x, "post_date_gmt":x,
                               "post_content":content, "post_title":chapitre_title, "post_excerpt":'', "post_status":'publish',
                               "comment_status":'open', "ping_status":'closed', "post_password":'', "post_name":chapitre_slug,
                               "to_ping":'', "pinged":'', "post_modified":x, "post_modified_gmt":x, "post_content_filtered":'',
                               "post_parent":'0', "guid":guid, "menu_order":'0', "post_type":'blog',
                               "post_mime_type":'', "comment_count":'0'

                    })
                    # commit explicitly
                    #connection.commit()
                    rey = posts.select().order_by(posts.columns.ID.desc()).limit(1)
                    sanaa = connection.execute(rey).fetchall()
                    chapitre_id = sanaa[0][0]
                    print(chapitre_id)
                    #add episode to category
                    '''
                    query = db.select([terms.columns.name, taxo.columns.term_taxonomy_id])
                    query = query.select_from(terms.join(taxo, and_(terms.columns.term_id == taxo.columns.term_id,
                                        terms.columns.name == manga_title)))
                    '''
                    #print(select(terms.c.name, taxo.c.term_taxonomy_id).join_from( terms, taxo  ))
                    result=select(terms.c.name, taxo.c.term_taxonomy_id).join_from(terms, taxo, and_(terms.c.term_id == taxo.c.term_id, terms.c.name == manga_title))
                    result_proxy = connection.execute(result) 
                    rows = result_proxy.fetchall()
                    print(rows)
                    cat_id= [row[1] for row in rows]
                    
                    #cat_id=cat_id[1]
                    connection.execute(term_rela.insert(), {"object_id":chapitre_id, "term_taxonomy_id":cat_id, "term_order":'0'})
                  
                    
                    '''
                    if chap_title:
                        connection.execute(postmeta.insert(), {"post_id":chapitre_id, "meta_key":'chapitre_title', "meta_value":chap_title})
                    '''
                    connection.execute(postmeta.insert(), {"post_id":chapitre_id, "meta_key":'chapter_number', "meta_value":chap_num})

def download_images_from_page(driver, page_num, chap_num, manga_path):
    button = driver.find_element(By.CSS_SELECTOR, "button.btn.dropdown-toggle.selectpicker")
    driver.execute_script("arguments[0].click();", button)
    time.sleep(2)
    nav = driver.find_elements(By.CSS_SELECTOR, '.dropdown-menu.inner.selectpicker li')
    page_element = nav[0]
    print(f' page element {page_element}')
    page_element.click()
    time.sleep(2)
    img_src=driver.find_element(By.CSS_SELECTOR,'.img-responsive.scan-page').get_attribute('src')
    print(f'link : {img_src}')
    img_url=img_src
    print(img_url)
    download_page_img(img_url=img_url,page_num=page_num,chap_num=chap_num,manga_path=manga_path)

def showsChapters(manga_url,start,end,manga_path):
  
    print(f"Starting showsChapters with start={start} and end={end}")
    unique_dir='C:\\Users\\weare\\AppData\\Roaming\\undetected_chromedriver\\chromedriver-win32'
    executable_path = os.path.join(unique_dir, 'chromedriver.exe')
    print(f' chrome : {executable_path}')
    chrome_options = uc.ChromeOptions() 
    extension_path = r'replace with ad block extension'
    chrome_options.add_argument( '--headless' )
    chrome_options.add_argument(f'--load-extension={extension_path}')
    driver = uc.Chrome(options=chrome_options,version_main=116,executable_path=executable_path)
    
    driver.get(manga_url)
    chapsurls=driver.find_elements(By.CSS_SELECTOR,'.chapters h5 ')
    chapsurls.reverse()
    nn=[]
    pp=[]
    processinf=chapsurls[start:end]
    bg=len(processinf)
    for g in range(bg):
                print(g)
                if g>=1:
                 
                 driver.get(manga_url)
                 chapsurls=driver.find_elements(By.CSS_SELECTOR,'.chapters h5 ')
                 chapsurls.reverse()
                 processinf=chapsurls[start:end]
                 
                chap_title=processinf[g].find_element(By.TAG_NAME,'em').text
                print(chap_title)
                chap_Url=processinf[g].find_element(By.TAG_NAME,'a').get_attribute('href')  
                driver.get(chap_Url)
                time.sleep(1)
                chap_num=chap_title.split(' Chapitre')[0].split(' ')[1]
                print(chap_Url)
                tittre=manga_path+' '+str(chap_num)+' VF'
                print(f'chapitre  title : {tittre}')
                print(tittre)
                nav=driver.find_elements(By.CSS_SELECTOR,'.dropdown-menu.inner.selectpicker li')
                
                imgs=[]
                for i,j in enumerate(nav):
                    
                    print(i)
                    print(j)
                    #time.sleep(2)
                    img_src=driver.find_element(By.CSS_SELECTOR,'.img-responsive.scan-page').get_attribute('src')
                    print(f'link : {img_src}')
                    img_url=img_src
                    
                    imgs.append(img_url)
                    
                    time.sleep(1)
                    button = driver.find_element(By.CSS_SELECTOR, ".page-nav ul.pager li.next a")
                    driver.execute_script("arguments[0].click();", button)                    
                    time.sleep(1)
                threads=[]
                # Create a thread pool executor
                max_threads = 5  # Number of concurrent threads
                executor = ThreadPoolExecutor(max_threads)

                for i,j in enumerate(imgs):
                    image_url=j
                    page_num=int(i)+1
                    #print(f'page numero {page_num}')
                    executor.submit(download_page_img,image_url,page_num,chap_num,manga_path)
                 

                # Shutdown the executor
                executor.shutdown()
                
def SendContent(directChap,pagename,sftp,content,content_lock,numbersofpages,manga_slug,chap_num,upath):
           
             
             result=[]
             filename=str(pagename)+'.jpg'
             for root, dir, files in os.walk(directChap):
                print(files)

                if filename in files:
                    result.append(os.path.join(root, filename))
                    print('ok')
       

             pagepath=result
             print('ss'+str(pagepath))
             
             picture=pagepath[0]
             print(f'pic : {picture}')
             image_name=str(manga_slug)+str(chap_num)+'page'+str(filename)
             print(f'fff {image_name}')
             server_path=upath+image_name
             urlImage='replace with website url'+str(image_name)
           
             with sftp_access_lock:
              try:
                sftp.put(picture,server_path)
              except Exception as e:
                print(e)
             jj=int(pagename)-1
            
             with content_lock:
            
                    content[jj]=str(urlImage)
                    
             
           
# Lock for controlling access to the sftp object
sftp_access_lock = threading.Lock()                    
def getContentpage(chapUrl,chap_num,sftp,manga_name,manga_path):
    chapitre_path='local path'
    upath='replace wwith ftp path'
    
    content_lock=threading.Lock()
    totalFiles = 0
    driver.get(chapUrl)
    time.sleep(3)
    x = datetime.datetime.now()
    directChap=os.path.join(chapitre_path,manga_path,str(chap_num))
    manga_slug=slugify(manga_name)
    for base, dirs, files in os.walk(directChap):
        print('Searching in : ',base)
        
        for Files in files:
            totalFiles += 1

    print('Total number of files',totalFiles)
    numbersofpages=int(totalFiles)+1
    print(f'ggg :{numbersofpages}')
    
    threads=[]
    max_threads = 5  
    executor = ThreadPoolExecutor(max_threads)
    content = [''] * (numbersofpages - 1)
    for i in range(1,numbersofpages):
        #page_num=int(i)+1
        executor.submit(SendContent,directChap,i,sftp,content,content_lock,numbersofpages,manga_slug,chap_num,upath)
    
    executor.shutdown()         
    sftp.close()   
        
    return content

if __name__ == '__main__':    
   
    urlChap='Replace_with_you_url'
    manga_name="replace with you manga"
    #manga_path='StarMartialGodTechnique'
    upath='replace with ftp path'
    url_manga=' '
    user_db = 'replace with your server database'
    db_mdp = 'replace with your server database'
    name_db = 'replace with your server database'
    ip = 'replace with your server database'
    wp = 'replace with your server database'
    site='replace with your server database'
    ftp_passe='replace with your server database'
    print(manga_name)
    result_queue = multiprocessing.Queue()
    pro1=multiprocessing.Process(target=showsChapters,args=(urlChap,30,45,manga_name))
    pro2=multiprocessing.Process(target=showsChapters,args=(urlChap,45,60,manga_name))
    pro1.start()
    pro2.start()
    pro1.join()
    pro2.join()    
    finish=time.perf_counter()
    chrome_options = uc.ChromeOptions() 
    extension_path = r'replace with add block extension'
    chrome_options.add_argument(f'--load-extension={extension_path}')
    driver = uc.Chrome(options=chrome_options,version_main=116)
    driver.get(urlChap)
    chapsurls=  driver.find_elements(By.CSS_SELECTOR,'.chapters h5 ')
    chapsurls.reverse()
    print(chapsurls)
    nn=[]
    pp=[]
    processinf=chapsurls[30:60]
    for chap in processinf:
        chapUrl=chap.find_element(By.TAG_NAME,'a').get_attribute('href')
        nn.append(chapUrl)
        print(chapUrl)
        chap_title=chap.find_element(By.TAG_NAME,'em').text
        pp.append(chap_title) 
    for g,i in enumerate(pp):
            engine,metadata,sftp=connectToWebsite(user_db =user_db ,db_mdp =db_mdp ,name_db=name_db,ip=ip ,wp=wp,site=site,ftp_passe=ftp_passe)  

            try:
                chap_title=i
            except Exception as e:
                print(e)
            chapUrl=nn[g]
            driver.get(chapUrl)
            time.sleep(2)
            chap_num=chap_title.split(' Chapitre')[0].split(' ')[1]
            print(chap_num)
            chapitre_path='replace with local path'
            directChap=os.path.join(chapitre_path,manga_name,str(chap_num))
            manga_slug=slugify(manga_name)
            print(manga_name)
            content=getContentpage(chapUrl,chap_num,sftp,manga_name,manga_name)
            content = '<--page-->'.join(content)
            print(f'final content : {content}')
            engine,metadata,sftp=connectToWebsite(user_db =user_db ,db_mdp =db_mdp ,name_db=name_db,ip=ip ,wp=wp,site=site,ftp_passe=ftp_passe)            
            addAllChapteronDB(chap_num,content,manga_name,chap_title,engine,metadata,sftp)
    
    