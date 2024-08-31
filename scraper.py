import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from PIL import Image

url = 'https://civitai.com/models/318927/faye-valentine-cowboy-bebop'
civitai = 'https://civitai.com'

def getMainImagesFromPage():
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    r = requests.get(url=url, headers=headers)
    # print(r.content)

    soup = BeautifulSoup(r.content, "html5lib")
    # print(soup.prettify())
    image_container = soup.find('div', attrs={'class': 'mantine-ContainerGrid-col mantine-1iztkyj'})
    carousel_images = image_container.findAll('div', attrs={'class': 'mantine-Carousel-slide mantine-h2ohe0'})

    for image in carousel_images:
        actual_image_div = image.find('img', attrs={'class': 'mantine-7aj0so'})
        if actual_image_div != None:
            #actual image source
            src = actual_image_div['src']

            im = Image.open(requests.get(src, stream=True).raw)
            im.show()


def getMainImagesAndPrompts():
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}
    r = requests.get(url=url, headers=headers)
    if r.status_code != 200:
        print(f"Error accessing URL: {url}")

    soup = BeautifulSoup(r.content, "html5lib")

    image_container = soup.find('div', attrs={'class': 'mantine-ContainerGrid-col mantine-1iztkyj'})
    if image_container is None:
        return
    
    carousel_images = image_container.findAll('div', attrs={'class': 'mantine-Carousel-slide mantine-h2ohe0'})

    driver = webdriver.Chrome()
    data = []
    for image in carousel_images:
        image_page_link_div = image.find('a', attrs={'class': 'mantine-Text-root mantine-Anchor-root mantine-1mvk3qi'})
        if image_page_link_div is None:
            continue

        #individual page for an image with its prompt, etc
        image_page_link = civitai + image_page_link_div['href']

        driver.get(image_page_link)
        html = driver.page_source
        soup2 = BeautifulSoup(html, "html5lib")

        # r2 = requests.get(url=image_page_link, headers=headers)
        # if r2.status_code != 200:
        #     print(f"Error accessing URL: {image_page_link}")
        #     continue

        # soup2 = BeautifulSoup(r2.content, "html5lib")
        curr_image_data = {}

        # GET IMAGE
        image_container2 = soup2.find('div', attrs={'class': 'flex min-h-0 flex-1 items-stretch justify-stretch'})
        if image_container2 is None:
            continue

        actual_image_tag = image_container2.find('img', attrs={'class': 'mantine-lrbwmi max-h-full w-auto max-w-full'})
        if actual_image_tag is None:
            continue

        # Actual image source
        src = actual_image_tag['src']
        # im = Image.open(requests.get(src, stream=True).raw)
        # im.show()

        curr_image_data['src'] = src

        # GET PROMPT, NEGATIVE PROMPT, MODELS USED, AND OTHER METADATA
        generation_data = soup2.findAll('div', attrs={'class': 'mantine-Paper-root mantine-Card-root flex flex-col gap-3 rounded-xl mantine-mp7k2v'})
        if generation_data is None:
            print("no generation data found")
            continue


        actualGenerationData = None
        for a in generation_data:
            spans = a.findAll('span')
            for span in spans:
                if span.get_text() == "Generation data":
                    actualGenerationData = a
                    break

            if actualGenerationData != None:
                break

        if actualGenerationData is None:
            continue

        generation_data = actualGenerationData

        generation_data_sections = generation_data.findAll('div', recursive=False)
        for section in generation_data_sections:
            title = section.find('div', attrs={'class': ['mantine-Text-root text-lg font-semibold mantine-ljqvxq', 'mantine-Text-root font-semibold mantine-ljqvxq']})
            if title is None:
                continue

            title = title.get_text()
            
            if title.lower() == 'resources used':
                print("case 1")

                models = []
                diff_models = section.findAll('li', attrs={'class': 'flex flex-col'})
                for m in diff_models:
                    nameURL = m.find('a', attrs={'class': 'mantine-Text-root cursor-pointer underline mantine-12h10m4'})
                    if nameURL is None:
                        continue

                    modelType = m.find('span', attrs={'class': 'mantine-h9iq4m mantine-Badge-inner'})
                    if modelType is None:
                        modelType = "None"
                    else:
                        modelType = modelType.get_text()

                    models.append({'name': nameURL.get_text(), 'url': civitai + nameURL['href'], 'type': modelType})

                curr_image_data['models'] = models

            elif title.lower() == 'prompt':
                print("case 2")

                prompt = section.find('div', attrs={'class': 'mantine-Text-root text-sm mantine-1c2skr8'})
                if prompt is None:
                    prompt = "None"
                else:
                    prompt = prompt.get_text()

                curr_image_data['prompt'] = prompt

            elif title.lower() == 'negative prompt':
                print("case 3")

                negPrompt = section.find('div', attrs={'class': 'mantine-Text-root text-sm mantine-1c2skr8'})
                if negPrompt is None:
                    negPrompt = "None"
                else:
                    negPrompt = negPrompt.get_text()

                curr_image_data['negative_prompt'] = negPrompt

            elif title.lower() == 'other metadata':
                print("case 4")

                metadata = {}
                diff_metadata = section.findAll('div', attrs={'class': 'flex justify-between gap-3'})
                for m in diff_metadata:
                    metadata_name = m.find('div', attrs={'class': 'mantine-Text-root text-nowrap leading-snug mantine-14lhcb9'})
                    metadata_val = m.find('div', attrs={'class': 'mantine-Text-root leading-snug mantine-ljqvxq'})
                    if metadata_name is None or metadata_val is None:
                        continue

                    metadata[metadata_name.get_text()] = metadata_val.get_text()

                curr_image_data['metadata'] = metadata

        data.append(curr_image_data)

    for d in data:
        print(d)
        print("<------------------------------------------------------------------------------------>")

getMainImagesAndPrompts()
            