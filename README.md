# His-Geo:  Geocoding the past world
<p align="center">
<a href="https://pypi.org/project/his_geo">
    <img src="https://img.shields.io/pypi/v/his_geo.svg" /></a>
<a href="http://www.apache.org/licenses/">
    <img src="https://img.shields.io/badge/License-MIT-green" /></a>
<a href="https://colab.research.google.com/github/yukiyuqichen/His-Geo/blob/main/evaluate.ipynb">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" /></a>
</p>

A library to extract historical toponyms from texts, geocode and visualize the results on maps.

## Install ##

```python
pip install his_geo --upgrade
```

## Import

```
from his_geo import extractor
from his_geo import geocoder
```

## Usage ##

### 1. Extractor: Extract toponyms and addresses from historical texts

#### 1.1 Set a prompt

```python
prompt = """
I would like you to take on the roles of both a Geographer and a Historian. 
You possess extensive knowledge in Chinese geography and history, with a particular expertise in historical toponymy. 
Your task is to extract precise location references of historical toponyms from texts.
When I provide a scholarly text analyzing the location of one or several historical toponyms, please identify and extract both the toponyms and their corresponding location references from the text. 
Keep the following in mind:
1. If the text presents differing opinions of the same historical toponym's location from various scholars, only extract the most correct location reference that the author of the text acknowledges or agrees with. Do not include location references that the author disputes.
2. If a toponym is mentioned in the text but no location is provided, please skip this toponym.
3. Present the extracted information always in Chinese and strictly adhere to the following format:
   "Toponym 1", "Location 1"
   "Toponym 2", "Location 2"
   Please do not include any explanation, verb or extraneous information.

The text is as follows:
         """
```

#### 1.2 Choose a Large Language Model and set your API key

```python
model = "chatgpt"
model_version = "gpt-3.5-turbo-1106"	# "gpt-4-1106-preview"
api_key = "Your API key"
```

Check the [OpenAI website](https://openai.com/blog/openai-api)

#### 1.3 Initialize an Extractor

```python
llm_extractor = extractor.Extractor(prompt, output_dir="The output directory", 
                                    model=model, model_version=model_version, 									            api_key=api_key)
```

#### 1.4 Load your data and run

Load from a CSV or EXCEL file:

```python
data = pd.read_csv("Your CSV file")		# data = pd.read_excel("Your EXCEL file")
texts = data["The Text Column"].tolist()
```

Run the extractor:

```python
results = llm_extractor.extract_texts(texts)
# Extracting text 0 to ./evaluation/extracted_results_chatgpt_gpt-4-1106-preview.json
# Extracting text 1 to ./evaluation/extracted_results_chatgpt_gpt-4-1106-preview.json
# Extracting text 2 to ./evaluation/extracted_results_chatgpt_gpt-4-1106-preview.json
# Extracting text 3 to ./evaluation/extracted_results_chatgpt_gpt-4-1106-preview.json
# Extracting text 4 to ./evaluation/extracted_results_chatgpt_gpt-4-1106-preview.json
# ......
```

The result will be automatically saved to the output_dir you set

#### 1.5 Check the result

```python
print(texts[0])
# '此为最早明确见于文献记载中的楚县，亦是春秋置县之首例。权本为子姓小国，后为楚武王所灭，并被改建为县。《左传》庄公十八年载：“初，楚武王克权，使斗缗尹之。”斗缗为楚国大夫，“尹之”，就是以斗缗为权县的长官，来管理县内的有关事务。楚武王在位时间为公元前740年至前690年。《水经·沔水注》曰：“沔水自荆城东南流，迳当阳县之章山东，山上有故城，太尉陶侃伐杜曾所筑也。……沔水又东，右会权口，水出章山，东南流权城北，古之权国也。”《大清一统志》卷342安陆府古迹权城下亦云：“在钟祥县西南。”是权县当位于今湖北省荆门县东南。杨伯峻《春秋左传注》以为在今湖北省当阳县东南，恐非，当是将古当阳县（位于今荆门县西南）与今当阳县错混而致误。后斗缗据权县而叛楚，楚武王率军“围而杀之”。随后“迁权于那处，使阎敖尹之”(《左传》庄公十八年)，即楚武王把权县原有的臣民迁往“那处”，并在那处设县，让阎敖为县尹，负责那处的地方政务。又，徐少华认为“迁权于那处”的应是指权国旧贵族及部分平民，在权县当仍有大多数平民留于当地而为县民，不可能全面迁走而使权成为弃地，权县仍当继续存在。其说恐未必与当时的事情发展相符。因权与那处颇近，权迁那处后，权已演变为一居民点，即一般的楚邑，而权县应当不复存在了。'
 
print(results[0])
# '权县,今湖北省荆门市东南'

```

### 2. Geocoder

#### 2.1 Load your data

Load from a CSV or EXCEL file:

```python
data = pd.read_csv("Your CSV file")		# data = pd.read_excel("Your EXCEL file")
addresses = data["The Address Column"].tolist()
```

#### 2.2 Initialize a geocoder

```python
geocoder_test = geocoder.Geocoder(addresses, 
                                  lang="ch",
                                  preferences=["modern", "historic"],
                                  if_certainty=True)
```

Only 'ch' (Chinese) can be used in lang for now.

#### 2.3 Run the goecoder

```python
# Addresses will be matched with locations in existing database after a process of toponym normalization
geocoder_test.match_address()

# Detect if there is any information about specific direction, to make the calculation more accurate
geocoder_test.detect_direction()

# Calculate a coordinate for each address
geocoder_test.calculate_point()
```

#### 2.4 Visualize the result on a map

```python
map = geocoder_test.visualize()
map
```

![](https://github.com/yukiyuqichen/Historical-Geocoder/blob/main/figures/visualization.png)

#### 2.5 Save the result

```python
geocoder_test.data.to_csv("The file path", encoding='utf-8-sig')
```

## Pipeline ##

![](https://github.com/yukiyuqichen/Historical-Geocoder/blob/main/figures/workflow.png)

### Toponym and Location Extraction

![](https://github.com/yukiyuqichen/His-Geo/blob/main/figures/extraction.png)

### Coordinate Calculation

![](https://github.com/yukiyuqichen/His-Geo/blob/main/figures/calculation_from_polygon.png)

![](https://github.com/yukiyuqichen/His-Geo/blob/main/figures/calculation_from_point.png)

![](https://github.com/yukiyuqichen/His-Geo/blob/main/figures/closeness.png)


## Case Study: Counties in the Spring and Autumn and Warring States periods (770 – 221 B.C.E.)

![](https://github.com/yukiyuqichen/His-Geo/blob/main/figures/maps.png)
