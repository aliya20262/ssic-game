from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json, asyncio, random, string, time
from typing import Dict

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Events with translations: en, ru, az
EVENTS = [
  {
    "type":{"en":"Crisis","ru":"Кризис","az":"Böhran"},
    "title":{"en":"Global market crash","ru":"Обвал мирового рынка","az":"Qlobal bazar çöküşü"},
    "desc":{"en":"Equity markets plunge 20%+ as recession fears explode. Credit markets seize and investors flee to safety.","ru":"Фондовые рынки падают на 20%+. Кредитные рынки замерзают, инвесторы уходят в защитные активы.","az":"Kapital bazarları 20%+ düşür. Kredit bazarları donur, investorlar təhlükəsiz aktivlərə qaçır."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Stocks -28%","c":"badge-red"},{"t":"ETFs -16%","c":"badge-red"},{"t":"Bonds +5%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"}],
             "ru":[{"t":"Акции -28%","c":"badge-red"},{"t":"ETF -16%","c":"badge-red"},{"t":"Облигации +5%","c":"badge-green"},{"t":"Нал. безопасны","c":"badge-gray"}],
             "az":[{"t":"Səhmlər -28%","c":"badge-red"},{"t":"ETF -16%","c":"badge-red"},{"t":"İstiqrazlar +5%","c":"badge-green"},{"t":"Nağd təhlükəsiz","c":"badge-gray"}]},
    "m":{"stocks":-.28,"bonds":.05,"etf":-.16,"deposit":.03,"cash":0}
  },
  {
    "type":{"en":"Macro","ru":"Макро","az":"Makro"},
    "title":{"en":"Inflation surges to 9%","ru":"Инфляция достигла 9%","az":"İnflyasiya 9%-ə çatdı"},
    "desc":{"en":"Consumer prices hit 40-year highs. Rate hike cycle begins and fixed income reprices sharply.","ru":"Потребительские цены на 40-летнем максимуме. Начинается цикл повышения ставок.","az":"İstehlak qiymətləri 40 illik rekorda çatdı. Faiz artırma dövrü başlayır."},
    "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
    "pills":{"en":[{"t":"Bonds -12%","c":"badge-red"},{"t":"Cash erodes","c":"badge-amber"},{"t":"Deposits +4%","c":"badge-green"},{"t":"Stocks flat","c":"badge-gray"}],
             "ru":[{"t":"Облигации -12%","c":"badge-red"},{"t":"Нал. обесцен.","c":"badge-amber"},{"t":"Депозиты +4%","c":"badge-green"},{"t":"Акции ровно","c":"badge-gray"}],
             "az":[{"t":"İstiqrazlar -12%","c":"badge-red"},{"t":"Nağd əriyir","c":"badge-amber"},{"t":"Depozit +4%","c":"badge-green"},{"t":"Səhmlər sabit","c":"badge-gray"}]},
    "m":{"stocks":.02,"bonds":-.12,"etf":-.03,"deposit":.04,"cash":-.02}
  },
  {
    "type":{"en":"Commodity","ru":"Сырьё","az":"Xammal"},
    "title":{"en":"Oil price spikes +60%","ru":"Нефть выросла на +60%","az":"Neft +60% bahalaşdı"},
    "desc":{"en":"Geopolitical tensions slash global supply. Energy names surge while transport and consumer sectors suffer.","ru":"Геополитика сокращает поставки нефти. Энергетика растёт, транспорт и потребители страдают.","az":"Geosiyasi gərginlik tədarükü azaldır. Enerji böyüyür, nəqliyyat və istehlak azalır."},
    "col":"#fffbeb","brd":"#fbbf24","tc":"#92400e",
    "pills":{"en":[{"t":"Energy +30%","c":"badge-green"},{"t":"ETFs +9%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Consumer down","c":"badge-red"}],
             "ru":[{"t":"Энергетика +30%","c":"badge-green"},{"t":"ETF +9%","c":"badge-green"},{"t":"Облигации ровно","c":"badge-gray"},{"t":"Потреб. -","c":"badge-red"}],
             "az":[{"t":"Enerji +30%","c":"badge-green"},{"t":"ETF +9%","c":"badge-green"},{"t":"İstiqrazlar sabit","c":"badge-gray"},{"t":"İstehlak aşağı","c":"badge-red"}]},
    "m":{"stocks":.09,"bonds":.01,"etf":.10,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Growth","ru":"Рост","az":"Artım"},
    "title":{"en":"AI technology boom","ru":"Бум ИИ-технологий","az":"Süni intellekt bumu"},
    "desc":{"en":"Breakthrough AI product goes viral. Tech earnings explode and investors flood equities and index funds.","ru":"Революционный ИИ-продукт стал вирусным. Прибыли технокомпаний взрываются.","az":"İnqilabi süni intellekt məhsulu viral oldu. Texnologiya gəlirləri partlayır."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"Stocks +32%","c":"badge-green"},{"t":"ETFs +19%","c":"badge-green"},{"t":"Bonds hold","c":"badge-gray"},{"t":"Economy up","c":"badge-green"}],
             "ru":[{"t":"Акции +32%","c":"badge-green"},{"t":"ETF +19%","c":"badge-green"},{"t":"Облигации держ.","c":"badge-gray"},{"t":"Экономика ↑","c":"badge-green"}],
             "az":[{"t":"Səhmlər +32%","c":"badge-green"},{"t":"ETF +19%","c":"badge-green"},{"t":"İstiqrazlar saxlayır","c":"badge-gray"},{"t":"İqtisadiyyat ↑","c":"badge-green"}]},
    "m":{"stocks":.33,"bonds":.01,"etf":.20,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Crisis","ru":"Кризис","az":"Böhran"},
    "title":{"en":"Banking sector collapse","ru":"Обвал банковского сектора","az":"Bank sektoru çöküşü"},
    "desc":{"en":"Three major banks fail overnight. Deposit insurance triggers and market-wide panic spreads rapidly.","ru":"Три крупных банка рухнули за ночь. Срабатывает страхование вкладов, паника охватывает рынок.","az":"Üç böyük bank bir gecədə çöküb. Depozit sığortası işə düşür, bazar paniklər."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Banks -35%","c":"badge-red"},{"t":"Bonds +8%","c":"badge-green"},{"t":"Deposits risky","c":"badge-amber"},{"t":"Cash is king","c":"badge-gray"}],
             "ru":[{"t":"Банки -35%","c":"badge-red"},{"t":"Облигации +8%","c":"badge-green"},{"t":"Депозиты риск","c":"badge-amber"},{"t":"Нал. — король","c":"badge-gray"}],
             "az":[{"t":"Banklar -35%","c":"badge-red"},{"t":"İstiqrazlar +8%","c":"badge-green"},{"t":"Depozit riskli","c":"badge-amber"},{"t":"Nağd — kral","c":"badge-gray"}]},
    "m":{"stocks":-.20,"bonds":.08,"etf":-.13,"deposit":-.06,"cash":.01}
  },
  {
    "type":{"en":"Policy","ru":"Политика","az":"Siyasət"},
    "title":{"en":"Interest rates jump +3%","ru":"Ставки выросли на +3%","az":"Faiz dərəcəsi +3% artdı"},
    "desc":{"en":"Central bank delivers a surprise jumbo rate hike. Bond prices crater and mortgage costs spike.","ru":"Центробанк неожиданно поднял ставку. Облигации падают, ипотека дорожает.","az":"Mərkəzi bank sürpriz faiz artışı etdi. İstiqraz qiymətləri düşür, ipoteka bahalaşır."},
    "col":"#eff6ff","brd":"#93c5fd","tc":"#1e40af",
    "pills":{"en":[{"t":"Bonds -14%","c":"badge-red"},{"t":"Deposits +7%","c":"badge-green"},{"t":"Stocks -6%","c":"badge-red"},{"t":"Cash ok","c":"badge-gray"}],
             "ru":[{"t":"Облигации -14%","c":"badge-red"},{"t":"Депозиты +7%","c":"badge-green"},{"t":"Акции -6%","c":"badge-red"},{"t":"Нал. ок","c":"badge-gray"}],
             "az":[{"t":"İstiqrazlar -14%","c":"badge-red"},{"t":"Depozit +7%","c":"badge-green"},{"t":"Səhmlər -6%","c":"badge-red"},{"t":"Nağd ok","c":"badge-gray"}]},
    "m":{"stocks":-.06,"bonds":-.14,"etf":-.05,"deposit":.07,"cash":.01}
  },
  {
    "type":{"en":"Macro","ru":"Макро","az":"Makro"},
    "title":{"en":"Sudden recession hits","ru":"Внезапная рецессия","az":"Gözlənilməz resessiya"},
    "desc":{"en":"GDP contracts two consecutive quarters. Unemployment surges to 8% and consumer spending collapses.","ru":"ВВП падает два квартала подряд. Безработица 8%, потребление рушится.","az":"ÜDM iki rüb ardıcıl azaldı. İşsizlik 8%-ə çatdı, istehlak çöküb."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Stocks -22%","c":"badge-red"},{"t":"ETFs -14%","c":"badge-red"},{"t":"Bonds +6%","c":"badge-green"},{"t":"Cash stable","c":"badge-gray"}],
             "ru":[{"t":"Акции -22%","c":"badge-red"},{"t":"ETF -14%","c":"badge-red"},{"t":"Облигации +6%","c":"badge-green"},{"t":"Нал. стабил.","c":"badge-gray"}],
             "az":[{"t":"Səhmlər -22%","c":"badge-red"},{"t":"ETF -14%","c":"badge-red"},{"t":"İstiqrazlar +6%","c":"badge-green"},{"t":"Nağd sabit","c":"badge-gray"}]},
    "m":{"stocks":-.22,"bonds":.06,"etf":-.14,"deposit":.03,"cash":0}
  },
  {
    "type":{"en":"Geopolitical","ru":"Геополитика","az":"Geosiyasət"},
    "title":{"en":"Political crisis erupts","ru":"Политический кризис","az":"Siyasi böhran"},
    "desc":{"en":"Constitutional crisis triggers snap elections. Foreign capital flees and currency devalues sharply.","ru":"Конституционный кризис. Иностранный капитал бежит, валюта девальвирует.","az":"Konstitusiya böhranı. Xarici kapital qaçır, valyuta kəskin ucuzlaşır."},
    "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
    "pills":{"en":[{"t":"Markets -12%","c":"badge-red"},{"t":"Bonds volatile","c":"badge-amber"},{"t":"Cash -2%","c":"badge-amber"},{"t":"Safe havens up","c":"badge-green"}],
             "ru":[{"t":"Рынки -12%","c":"badge-red"},{"t":"Облиг. волат.","c":"badge-amber"},{"t":"Нал. -2%","c":"badge-amber"},{"t":"Защит. активы ↑","c":"badge-green"}],
             "az":[{"t":"Bazarlar -12%","c":"badge-red"},{"t":"İstiqrazlar dəyişkən","c":"badge-amber"},{"t":"Nağd -2%","c":"badge-amber"},{"t":"Təhlükəsiz aktivlər ↑","c":"badge-green"}]},
    "m":{"stocks":-.12,"bonds":-.07,"etf":-.10,"deposit":.01,"cash":-.02}
  },
  {
    "type":{"en":"Tech","ru":"Технологии","az":"Texnologiya"},
    "title":{"en":"Crypto market meltdown","ru":"Крах криптовалютного рынка","az":"Kripto bazar çöküşü"},
    "desc":{"en":"Major stablecoin depegs. Crypto contagion spreads to tech stocks and risk assets globally.","ru":"Крупный стейблкоин потерял привязку. Крипто-зараза распространяется на техно-акции.","az":"Böyük stablecoin öz bağlılığını itirdi. Kripto yoluxması texnologiya səhmlərinə yayılır."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Tech -18%","c":"badge-red"},{"t":"Bonds +4%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"},{"t":"Deposits ok","c":"badge-green"}],
             "ru":[{"t":"Технологии -18%","c":"badge-red"},{"t":"Облигации +4%","c":"badge-green"},{"t":"Нал. безоп.","c":"badge-gray"},{"t":"Депозиты ок","c":"badge-green"}],
             "az":[{"t":"Texnologiya -18%","c":"badge-red"},{"t":"İstiqrazlar +4%","c":"badge-green"},{"t":"Nağd təhlükəsiz","c":"badge-gray"},{"t":"Depozit ok","c":"badge-green"}]},
    "m":{"stocks":-.18,"bonds":.04,"etf":-.12,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Growth","ru":"Рост","az":"Artım"},
    "title":{"en":"Green energy revolution","ru":"Революция зелёной энергетики","az":"Yaşıl enerji inqilabı"},
    "desc":{"en":"Historic climate bill passes. Renewable energy stocks surge. Fossil fuel divestment accelerates.","ru":"Принят исторический климатический закон. Возобновляемая энергетика взлетает.","az":"Tarixi iqlim qanunu qəbul edildi. Bərpa olunan enerji səhmləri sürətlə artır."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"Green stocks +35%","c":"badge-green"},{"t":"ETFs +12%","c":"badge-green"},{"t":"Oil sector -15%","c":"badge-red"},{"t":"Bonds steady","c":"badge-gray"}],
             "ru":[{"t":"Зелёные акции +35%","c":"badge-green"},{"t":"ETF +12%","c":"badge-green"},{"t":"Нефть -15%","c":"badge-red"},{"t":"Облигации стаб.","c":"badge-gray"}],
             "az":[{"t":"Yaşıl səhmlər +35%","c":"badge-green"},{"t":"ETF +12%","c":"badge-green"},{"t":"Neft -15%","c":"badge-red"},{"t":"İstiqrazlar sabit","c":"badge-gray"}]},
    "m":{"stocks":.22,"bonds":.01,"etf":.13,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Crisis","ru":"Кризис","az":"Böhran"},
    "title":{"en":"Trade war escalates","ru":"Эскалация торговой войны","az":"Ticarət müharibəsi genişlənir"},
    "desc":{"en":"Major economies impose sweeping tariffs. Supply chains collapse. Global trade volumes drop 15%.","ru":"Крупные экономики вводят масштабные тарифы. Цепочки поставок рушатся.","az":"Böyük iqtisadiyyatlar geniş tariflər tətbiq edir. Təchizat zəncirləri çöküb."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Stocks -19%","c":"badge-red"},{"t":"ETFs -11%","c":"badge-red"},{"t":"Bonds +3%","c":"badge-green"},{"t":"Cash safe","c":"badge-gray"}],
             "ru":[{"t":"Акции -19%","c":"badge-red"},{"t":"ETF -11%","c":"badge-red"},{"t":"Облигации +3%","c":"badge-green"},{"t":"Нал. безоп.","c":"badge-gray"}],
             "az":[{"t":"Səhmlər -19%","c":"badge-red"},{"t":"ETF -11%","c":"badge-red"},{"t":"İstiqrazlar +3%","c":"badge-green"},{"t":"Nağd təhlükəsiz","c":"badge-gray"}]},
    "m":{"stocks":-.19,"bonds":.03,"etf":-.11,"deposit":.02,"cash":.01}
  },
  {
    "type":{"en":"Growth","ru":"Рост","az":"Artım"},
    "title":{"en":"Biotech breakthrough","ru":"Прорыв в биотехнологиях","az":"Biotexnologiya irəliləyişi"},
    "desc":{"en":"Revolutionary cancer treatment approved. Pharmaceutical stocks surge. Healthcare sector leads rally.","ru":"Революционное лечение рака одобрено. Фармацевтические акции взлетают.","az":"İnqilabi xərçəng müalicəsi təsdiqləndi. Əczaçılıq səhmləri sürətlə artır."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"Biotech +40%","c":"badge-green"},{"t":"ETFs +14%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Economy grows","c":"badge-green"}],
             "ru":[{"t":"Биотех +40%","c":"badge-green"},{"t":"ETF +14%","c":"badge-green"},{"t":"Облигации ровно","c":"badge-gray"},{"t":"Экономика растёт","c":"badge-green"}],
             "az":[{"t":"Biotex +40%","c":"badge-green"},{"t":"ETF +14%","c":"badge-green"},{"t":"İstiqrazlar sabit","c":"badge-gray"},{"t":"İqtisadiyyat böyüyür","c":"badge-green"}]},
    "m":{"stocks":.28,"bonds":.01,"etf":.15,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Macro","ru":"Макро","az":"Makro"},
    "title":{"en":"Unemployment hits 12%","ru":"Безработица достигла 12%","az":"İşsizlik 12%-ə çatdı"},
    "desc":{"en":"Mass layoffs sweep tech and manufacturing. Consumer confidence collapses. Spending contracts sharply.","ru":"Массовые увольнения в технологиях и производстве. Потребительская уверенность рухнула.","az":"Texnologiya və istehsalda kütləvi ixtisar. İstehlakçı etimadı çöküb."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Stocks -16%","c":"badge-red"},{"t":"Bonds +5%","c":"badge-green"},{"t":"ETFs -10%","c":"badge-red"},{"t":"Cash stable","c":"badge-gray"}],
             "ru":[{"t":"Акции -16%","c":"badge-red"},{"t":"Облигации +5%","c":"badge-green"},{"t":"ETF -10%","c":"badge-red"},{"t":"Нал. стабил.","c":"badge-gray"}],
             "az":[{"t":"Səhmlər -16%","c":"badge-red"},{"t":"İstiqrazlar +5%","c":"badge-green"},{"t":"ETF -10%","c":"badge-red"},{"t":"Nağd sabit","c":"badge-gray"}]},
    "m":{"stocks":-.16,"bonds":.05,"etf":-.10,"deposit":.03,"cash":0}
  },
  {
    "type":{"en":"Policy","ru":"Политика","az":"Siyasət"},
    "title":{"en":"Central bank cuts rates -2%","ru":"ЦБ снизил ставки на -2%","az":"Mərkəzi bank faizi -2% azaltdı"},
    "desc":{"en":"Emergency rate cuts to fight recession. Bond prices surge. Banks increase lending aggressively.","ru":"Экстренное снижение ставок. Облигации растут, банки наращивают кредитование.","az":"Resessiyaya qarşı təcili faiz azaldılması. İstiqrazlar artır, banklar kreditləri artırır."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"Bonds +15%","c":"badge-green"},{"t":"Stocks +8%","c":"badge-green"},{"t":"ETFs +10%","c":"badge-green"},{"t":"Deposits -3%","c":"badge-red"}],
             "ru":[{"t":"Облигации +15%","c":"badge-green"},{"t":"Акции +8%","c":"badge-green"},{"t":"ETF +10%","c":"badge-green"},{"t":"Депозиты -3%","c":"badge-red"}],
             "az":[{"t":"İstiqrazlar +15%","c":"badge-green"},{"t":"Səhmlər +8%","c":"badge-green"},{"t":"ETF +10%","c":"badge-green"},{"t":"Depozit -3%","c":"badge-red"}]},
    "m":{"stocks":.08,"bonds":.15,"etf":.10,"deposit":-.03,"cash":0}
  },
  {
    "type":{"en":"Geopolitical","ru":"Геополитика","az":"Geosiyasət"},
    "title":{"en":"Regional war breaks out","ru":"Начался региональный конфликт","az":"Regional müharibə başladı"},
    "desc":{"en":"Armed conflict erupts in a major oil-producing region. Defense stocks surge. Energy prices spike.","ru":"Вооружённый конфликт в нефтедобывающем регионе. Оборонные акции взлетают.","az":"Böyük neft istehsalı bölgəsində silahlı münaqişə. Müdafiə səhmləri sürətlə artır."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Defense +25%","c":"badge-green"},{"t":"Oil +40%","c":"badge-green"},{"t":"Markets -14%","c":"badge-red"},{"t":"Bonds +4%","c":"badge-green"}],
             "ru":[{"t":"Оборона +25%","c":"badge-green"},{"t":"Нефть +40%","c":"badge-green"},{"t":"Рынки -14%","c":"badge-red"},{"t":"Облигации +4%","c":"badge-green"}],
             "az":[{"t":"Müdafiə +25%","c":"badge-green"},{"t":"Neft +40%","c":"badge-green"},{"t":"Bazarlar -14%","c":"badge-red"},{"t":"İstiqrazlar +4%","c":"badge-green"}]},
    "m":{"stocks":-.08,"bonds":.04,"etf":-.06,"deposit":.02,"cash":.01}
  },
  {
    "type":{"en":"Growth","ru":"Рост","az":"Artım"},
    "title":{"en":"Space economy takes off","ru":"Космическая экономика взлетает","az":"Kosmik iqtisadiyyat inkişaf edir"},
    "desc":{"en":"First commercial space station launches. Satellite internet reaches 3 billion users. Space ETFs explode.","ru":"Первая коммерческая космическая станция запущена. Спутниковый интернет охватывает 3 млрд пользователей.","az":"İlk kommersiya kosmik stansiyası işə salındı. Peyk interneti 3 milyard istifadəçiyə çatdı."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"Tech +28%","c":"badge-green"},{"t":"ETFs +16%","c":"badge-green"},{"t":"Bonds flat","c":"badge-gray"},{"t":"Economy booms","c":"badge-green"}],
             "ru":[{"t":"Технологии +28%","c":"badge-green"},{"t":"ETF +16%","c":"badge-green"},{"t":"Облигации ровно","c":"badge-gray"},{"t":"Экономика бумит","c":"badge-green"}],
             "az":[{"t":"Texnologiya +28%","c":"badge-green"},{"t":"ETF +16%","c":"badge-green"},{"t":"İstiqrazlar sabit","c":"badge-gray"},{"t":"İqtisadiyyat bum","c":"badge-green"}]},
    "m":{"stocks":.28,"bonds":.01,"etf":.16,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Crisis","ru":"Кризис","az":"Böhran"},
    "title":{"en":"Sovereign debt default","ru":"Суверенный дефолт","az":"Suveren borc defoltı"},
    "desc":{"en":"Major emerging market defaults on $500B debt. Contagion spreads to European bond markets.","ru":"Крупный развивающийся рынок объявил дефолт на $500 млрд. Зараза переходит на европейские облигации.","az":"Böyük inkişaf etməkdə olan bazar 500 milyard dollar borca defolt elan etdi."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"EM stocks -30%","c":"badge-red"},{"t":"Bonds -8%","c":"badge-red"},{"t":"ETFs -12%","c":"badge-red"},{"t":"Cash safe","c":"badge-gray"}],
             "ru":[{"t":"Акции EM -30%","c":"badge-red"},{"t":"Облигации -8%","c":"badge-red"},{"t":"ETF -12%","c":"badge-red"},{"t":"Нал. безоп.","c":"badge-gray"}],
             "az":[{"t":"EM səhmləri -30%","c":"badge-red"},{"t":"İstiqrazlar -8%","c":"badge-red"},{"t":"ETF -12%","c":"badge-red"},{"t":"Nağd təhlükəsiz","c":"badge-gray"}]},
    "m":{"stocks":-.24,"bonds":-.08,"etf":-.12,"deposit":.01,"cash":.02}
  },
  {
    "type":{"en":"Macro","ru":"Макро","az":"Makro"},
    "title":{"en":"Supply chain crisis","ru":"Кризис цепочек поставок","az":"Təchizat zənciri böhranı"},
    "desc":{"en":"Global shipping disrupted by port strikes. Inflation spikes. Production halts worldwide.","ru":"Глобальные поставки нарушены забастовками в портах. Инфляция резко растёт.","az":"Liman tətilləri qlobal daşımaları pozdu. İnflyasiya kəskin artır."},
    "col":"#fffbeb","brd":"#fcd34d","tc":"#92400e",
    "pills":{"en":[{"t":"Stocks -8%","c":"badge-red"},{"t":"ETFs -5%","c":"badge-red"},{"t":"Commodities +20%","c":"badge-green"},{"t":"Deposits ok","c":"badge-gray"}],
             "ru":[{"t":"Акции -8%","c":"badge-red"},{"t":"ETF -5%","c":"badge-red"},{"t":"Сырьё +20%","c":"badge-green"},{"t":"Депозиты ок","c":"badge-gray"}],
             "az":[{"t":"Səhmlər -8%","c":"badge-red"},{"t":"ETF -5%","c":"badge-red"},{"t":"Xammal +20%","c":"badge-green"},{"t":"Depozit ok","c":"badge-gray"}]},
    "m":{"stocks":-.08,"bonds":-.03,"etf":-.05,"deposit":.03,"cash":-.01}
  },
  {
    "type":{"en":"Growth","ru":"Рост","az":"Artım"},
    "title":{"en":"Electric vehicle revolution","ru":"Революция электромобилей","az":"Elektrik avtomobili inqilabı"},
    "desc":{"en":"EV sales overtake combustion engines. Battery costs collapse 80%. Auto and energy sectors transform.","ru":"Продажи электромобилей обгоняют ДВС. Стоимость батарей падает на 80%.","az":"Elektrik avtomobili satışları yanacaqla işləyən mühərrikləri ötdü. Batareya xərcləri 80% azaldı."},
    "col":"#f0fdf4","brd":"#86efac","tc":"#166534",
    "pills":{"en":[{"t":"EV stocks +45%","c":"badge-green"},{"t":"ETFs +18%","c":"badge-green"},{"t":"Oil down","c":"badge-red"},{"t":"Bonds steady","c":"badge-gray"}],
             "ru":[{"t":"Электромоб. +45%","c":"badge-green"},{"t":"ETF +18%","c":"badge-green"},{"t":"Нефть вниз","c":"badge-red"},{"t":"Облигации стаб.","c":"badge-gray"}],
             "az":[{"t":"EV səhmləri +45%","c":"badge-green"},{"t":"ETF +18%","c":"badge-green"},{"t":"Neft aşağı","c":"badge-red"},{"t":"İstiqrazlar sabit","c":"badge-gray"}]},
    "m":{"stocks":.25,"bonds":.01,"etf":.18,"deposit":.02,"cash":0}
  },
  {
    "type":{"en":"Crisis","ru":"Кризис","az":"Böhran"},
    "title":{"en":"Cyberattack on banks","ru":"Кибератака на банки","az":"Banklara kiberhücum"},
    "desc":{"en":"Coordinated attack hits 50 major banks. ATMs go dark. Online payments freeze for 48 hours.","ru":"Скоординированная атака на 50 крупных банков. Банкоматы отключены. Онлайн-платежи заморожены.","az":"50 böyük banka koordinasiyalı hücum. Bankomatlar söndürüldü. Onlayn ödənişlər 48 saat dondu."},
    "col":"#fef2f2","brd":"#f87171","tc":"#991b1b",
    "pills":{"en":[{"t":"Banks -22%","c":"badge-red"},{"t":"Stocks -10%","c":"badge-red"},{"t":"Cash king","c":"badge-green"},{"t":"Bonds +3%","c":"badge-green"}],
             "ru":[{"t":"Банки -22%","c":"badge-red"},{"t":"Акции -10%","c":"badge-red"},{"t":"Нал. — король","c":"badge-green"},{"t":"Облигации +3%","c":"badge-green"}],
             "az":[{"t":"Banklar -22%","c":"badge-red"},{"t":"Səhmlər -10%","c":"badge-red"},{"t":"Nağd — kral","c":"badge-green"},{"t":"İstiqrazlar +3%","c":"badge-green"}]},
    "m":{"stocks":-.15,"bonds":.03,"etf":-.10,"deposit":-.04,"cash":.03}
  },
]

AVATAR_COLORS = [
    "#2563eb","#059669","#dc2626","#d97706","#7c3aed","#0891b2",
    "#db2777","#65a30d","#ea580c","#0f766e","#7c2d12","#1e40af",
    "#166534","#991b1b","#92400e","#4c1d95","#164e63","#881337",
    "#3f6212","#78350f","#1d4ed8","#047857","#b91c1c","#b45309",
    "#6d28d9","#0e7490","#be185d","#4d7c0f","#c2410c","#0f766e",
    "#312e81","#064e3b","#7f1d1d","#451a03","#1e1b4b","#022c22",
    "#4a1942","#0c4a6e","#14532d","#431407"
]

rooms: Dict[str, dict] = {}
connections: Dict[str, Dict[str, WebSocket]] = {}
host_connections: Dict[str, WebSocket] = {}

def gen_code():
    return ''.join(random.choices(string.ascii_uppercase, k=4))

def new_room(host_password, total_rounds, diff):
    code = gen_code()
    while code in rooms:
        code = gen_code()
    evs = random.sample(EVENTS, min(total_rounds, len(EVENTS)))
    return {
        "code": code, "host_password": host_password,
        "phase": "lobby", "round": 0, "total_rounds": total_rounds, "diff": diff,
        "event_queue": evs, "players": {}, "created_at": time.time(),
    }

def new_player(name, color):
    return {
        "name": name, "color": color,
        "initials": ''.join([w[0] for w in name.strip().split() if w])[:2].upper() or "?",
        "capital": 10000, "history": [10000],
        "alloc": {"stocks":0,"bonds":0,"etf":0,"deposit":0,"cash":0},
        "round_done": False, "decisions": [], "confirmed_alloc": False,
        "badge": None,
    }

async def broadcast_room(code, msg):
    dead = []
    for pid, ws in connections.get(code, {}).items():
        try:
            await ws.send_text(json.dumps(msg))
        except:
            dead.append(pid)
    for pid in dead:
        connections.get(code, {}).pop(pid, None)

async def send_host(code, msg):
    ws = host_connections.get(code)
    if ws:
        try:
            await ws.send_text(json.dumps(msg))
        except:
            host_connections.pop(code, None)

async def broadcast_state(code):
    room = rooms.get(code)
    if not room:
        return
    state = room_state(room)
    await broadcast_room(code, {"type": "state", "data": state})
    await send_host(code, {"type": "state", "data": state})

def room_state(room):
    ev_idx = room["round"] - 1
    current_event = None
    if 0 <= ev_idx < len(room["event_queue"]):
        current_event = room["event_queue"][ev_idx]
    return {
        "code": room["code"], "phase": room["phase"],
        "round": room["round"], "total_rounds": room["total_rounds"],
        "diff": room["diff"], "current_event": current_event,
        "players": room["players"],
    }

def assign_badges(room):
    players = list(room["players"].values())
    if not players:
        return
    sorted_p = sorted(players, key=lambda p: p["capital"], reverse=True)
    for i, p in enumerate(sorted_p):
        ret = (p["capital"] - 10000) / 10000
        if i == 0:
            p["badge"] = "champion"
        elif ret > 0.15:
            p["badge"] = "bull"
        elif ret < -0.15:
            p["badge"] = "bear"
        elif abs(ret) < 0.03:
            p["badge"] = "steady"
        else:
            p["badge"] = "learner"

@app.post("/api/create-room")
async def create_room(body: dict):
    password = body.get("password", "").strip()
    total_rounds = max(3, min(15, int(body.get("total_rounds", 6))))
    diff = body.get("diff", "medium")
    if not password:
        raise HTTPException(400, "Password required")
    room = new_room(password, total_rounds, diff)
    rooms[room["code"]] = room
    connections[room["code"]] = {}
    return {"code": room["code"]}

@app.post("/api/join-room")
async def join_room(body: dict):
    code = body.get("code", "").strip().upper()
    name = body.get("name", "").strip()
    if not code or not name:
        raise HTTPException(400, "Code and name required")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    if room["phase"] == "final":
        raise HTTPException(400, "Game already ended")
    if len(room["players"]) >= 100:
        raise HTTPException(400, "Room is full (100 max)")
    if name.lower() in [p["name"].lower() for p in room["players"].values()]:
        raise HTTPException(400, "Name already taken")
    color = AVATAR_COLORS[len(room["players"]) % len(AVATAR_COLORS)]
    pid = f"p_{int(time.time()*1000)}_{random.randint(1000,9999)}"
    room["players"][pid] = new_player(name, color)
    await broadcast_state(code)
    return {"pid": pid, "color": color, "name": name}

@app.post("/api/host-action")
async def host_action(body: dict):
    code = body.get("code", "").upper()
    password = body.get("password", "")
    action = body.get("action", "")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    if room["host_password"] != password:
        raise HTTPException(403, "Wrong password")
    if action == "start":
        if not room["players"]:
            raise HTTPException(400, "No players")
        room["phase"] = "alloc"
        room["round"] = 1
        for p in room["players"].values():
            p["round_done"] = False
            p["confirmed_alloc"] = False
        await broadcast_state(code)
    elif action == "next_round":
        if room["round"] >= room["total_rounds"]:
            assign_badges(room)
            room["phase"] = "final"
        else:
            room["round"] += 1
            room["phase"] = "alloc"
            for p in room["players"].values():
                p["round_done"] = False
                p["confirmed_alloc"] = False
        await broadcast_state(code)
    elif action == "start_event":
        room["phase"] = "event"
        for p in room["players"].values():
            p["round_done"] = False
        await broadcast_state(code)
        asyncio.create_task(watch_round(code))
    elif action == "end":
        assign_badges(room)
        room["phase"] = "final"
        await broadcast_state(code)
    return {"ok": True}

async def watch_round(code):
    room = rooms.get(code)
    if not room:
        return
    diff_times = {"easy": 62, "medium": 32, "hard": 17}
    wait = diff_times.get(room.get("diff", "medium"), 32)
    for _ in range(wait * 2):
        await asyncio.sleep(0.5)
        room = rooms.get(code)
        if not room or room["phase"] != "event":
            return
        if all(p["round_done"] for p in room["players"].values()):
            room["phase"] = "result"
            await broadcast_state(code)
            return
    room = rooms.get(code)
    if room and room["phase"] == "event":
        for p in room["players"].values():
            if not p["round_done"]:
                apply_action(room, p, "hold")
        room["phase"] = "result"
        await broadcast_state(code)

def apply_action(room, player, action):
    ev_idx = room["round"] - 1
    if ev_idx < 0 or ev_idx >= len(room["event_queue"]):
        return
    ev = room["event_queue"][ev_idx]
    mod = 0.45 if action == "sell" else 1.55 if action == "buy" else 1.0
    alloc = player["alloc"]
    total_alloc = sum(alloc.values())
    nc = 0
    for asset_id, pct in alloc.items():
        share = player["capital"] * pct / 100
        nc += share * (1 + ev["m"][asset_id] * mod)
    nc += player["capital"] * (1 - total_alloc / 100)
    nc = max(100, round(nc))
    delta = nc - player["capital"]
    player["capital"] = nc
    player["history"].append(nc)
    player["round_done"] = True
    player["decisions"].append({"round": room["round"], "action": action, "delta": delta})

@app.post("/api/player-action")
async def player_action(body: dict):
    code = body.get("code", "").upper()
    pid = body.get("pid", "")
    action_type = body.get("action", "")
    room = rooms.get(code)
    if not room:
        raise HTTPException(404, "Room not found")
    player = room["players"].get(pid)
    if not player:
        raise HTTPException(404, "Player not found")
    if action_type == "set_alloc":
        alloc = body.get("alloc", {})
        if sum(alloc.values()) > 100:
            raise HTTPException(400, "Allocation exceeds 100%")
        player["alloc"] = alloc
        player["confirmed_alloc"] = True
        await broadcast_state(code)
    elif action_type in ("sell", "hold", "buy"):
        if player["round_done"]:
            raise HTTPException(400, "Already acted")
        if room["phase"] != "event":
            raise HTTPException(400, "Not in event phase")
        apply_action(room, player, action_type)
        if all(p["round_done"] for p in room["players"].values()):
            room["phase"] = "result"
        await broadcast_state(code)
    return {"ok": True, "capital": player.get("capital", 10000)}

@app.get("/api/room/{code}")
async def get_room(code: str):
    room = rooms.get(code.upper())
    if not room:
        raise HTTPException(404, "Room not found")
    return room_state(room)

@app.websocket("/ws/{code}/{pid}")
async def ws_player(websocket: WebSocket, code: str, pid: str):
    code = code.upper()
    await websocket.accept()
    if code not in connections:
        connections[code] = {}
    connections[code][pid] = websocket
    room = rooms.get(code)
    if room:
        await websocket.send_text(json.dumps({"type": "state", "data": room_state(room)}))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.get(code, {}).pop(pid, None)

@app.websocket("/ws-host/{code}")
async def ws_host(websocket: WebSocket, code: str):
    code = code.upper()
    await websocket.accept()
    host_connections[code] = websocket
    room = rooms.get(code)
    if room:
        await websocket.send_text(json.dumps({"type": "state", "data": room_state(room)}))
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        host_connections.pop(code, None)

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
