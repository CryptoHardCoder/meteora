# 🤖 Meteora DLMM JLP-USDT
Софт написан для автомотизации открытия и закрытия позиций по установленному ренйджу на defi площадке meteora 

## 🛠 Что делает софт?
*✅ открывает профиль adspower*

*✅ идет на meteora.ag*

*✅ Открывает DLMM страницу* 

*✅ находит первый пулл по паре JLP-USDT, обычно только в первом вся ликвидность собрана*

*✅ переходить в пулл*

*✅ проверяет есть ли у вам там позиции, если нет позиции, то открывает, ориентируясь от ваших настроек(ниже будет все настройки и инструкция по ним)*

*~✅ если цена пойдет в право на 95% от цены открытия графика, софт закрывает позицию и открывает новую позицию~*

*~✅ если цена пойдет в лево, на 90% приблизиться к минимальной цене, софт закрывает позицию и открывает новую позицию~*

*✅ и так до бесконечности с проверкой в определенное время.*

## UPDATE 17.09.24

*✅ софт проверяет страницу сайта на наличие предупреждении с расхождением цены, если есть, засыпает на 2 минуты, и проверяет еще раз при добавлении позиций*

*✅ если цена пойдет в право и дойдет до края графика, софт закрывает позицию и открывает новую позицию*

*✅ теперь можно настроить процент рейджа цены при открытии позиции*

## UPDATE 01.10.24

*✅ Добавлена функция записи истории позиций в отдельный файл для удобного отслеживания всех выполненных действий*

*✅ Реализованы уведомления через Telegram-бота при внезапной или запланированной остановке программы (опционально, если не требуется уведомление, настройка не обязательна)*

*✅ Зафиксированы и устранены критические моменты на сайте, которые ранее приводили к сбоям в работе программы*

*✅ Софт адаптирована под любые размеры окна браузера, теперь она корректно работает независимо от выбранного разрешения*

*✅ При падении баланса SOL ниже 0.08 софт сначала проверяет баланс USDT. Если на счету больше 5 USDT, происходит обмен на SOL. 
Если USDT меньше 5, проверяется баланс JLP. При наличии более 2 JLP они конвертируются в SOL, чтобы достичь 0.08 SOL на балансе*

*✅ Добавлена функция закрытие всех страниц перед началом работы софта. Сделано для того чтобы софт не путался среди похожих страниц, они могут привести к сбою работы софта*

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# ОБЯЗАТЕЛЬНЫЕ УСЛОВИЯ ДЛЯ ПОЛНОЦЕННОЙ РАБОТЫ СОФТА:
1) Для работы софта у вам должен быть ADSPOWER и хотя бы один профиль. Софт рассчитан на работу с одним профилем, а не с фермой

2) До запуска софта ВАМ надо самим запускать ADSPOWER, софт может только профиль запускать, но антик не сможет!!!

3) Софт работает с кошельком SOLFLARE, если у вас другой кошелек, просим установить SOLFLARE

--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 🚀 Установка и запуск
### 🐍 Установка Python
1. Перейдите на [официальный сайт Python 3.11](https://www.python.org/downloads/release/python-3119/)
2. В разделе "Files" выберите подходящий вариант для вашей операционной системы
3. Запустите установщик и обязательно поставьте галочку "Add Python to PATH"


### 🤖 Установка бота
1. На GitHub нажмите кнопку "Code" -> "Download ZIP" и разархивируйте в выбранную папку
2. Откройте терминал и перейдите в папку с ботом: `cd "path/to/bot"`, где `path/to/bot` - путь к папке с ботом
3. Установите все зависимости: `pip install -r requirements.txt`
4. Найдите файл с названием setting.py и заполните поля. Инструкция как заполнить будет ниже ⬇️
5. Запустите бота командой: `python main.py`

## 📋 Как настроить 'setting.py'
#### ОБРАЩАЕМ ВНИМАНИЕ НА КАВЫЧКИ, ЕСЛИ ГДЕ-ТО ДОБАВИТЕ ИЛИ ЗАБУДЕТЕ УКАЗАТЬ КАВЫЧКИ, СОФТ НЕ БУДЕТ РАБОТАТЬ!
#### Кошелек Solflare на русском языку должно быть!!!

```python 
adspower_api_url = "скопированный url сюда вставляем/api/v1/browser/start"
```
+ Здесь указываем url api от ADSPOWER. Открываем в adsposwer, слева в разделе 'Автомотизация' нажимаем 'API', 
+ там либо надо будет на первую кнопку Соединение, либо уже будет открыто ссылка. Пример ссыллки: http://local.adspower.net:12345.
+ Копируем и вставляем до '/api/v1/browser/start'ГОТОВА!
  ![Скриншот ADS URL]([https://github.com/Kuba199403/meteora/issues/1#issuecomment-2350105124](https://github.com/Kuba199403/meteora/blob/main/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202024-09-13%20%D0%B2%2022.13.13.png))

``` python
adspower_api_key = "ваш API KEY"
```
+ Теперь там где мы брали верхнюю ссылку, снизу этой ссылки будет кнопка API KEY: если у вас создано ранее, 
+ будет написано 'Создано', если знаете то пишите сюда, если забыли, нажимаем 'Сбросить' и полученный ключ УКАЗЫВАЕМ В КАВЫЧКАХ ОБЯЗАТЕЛЬНО!!!
![Скриншот ADS API]([https://github.com/Kuba199403/meteora/issues/1#issue-2525631916](https://github.com/Kuba199403/meteora/blob/main/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202024-09-13%20%D0%B2%2022.21.31.png))
``` python
private_key = 'private_key'
```
+ Теперь в adspower заходим в 'ПРОФИЛИ', выбираем тот профил с которым будем работать. 
+ У каждого профиля есть свое имя, ip, ...., и есть Nomer ID из семи символов, это то что нам надо
копируем и вставлем между кавычек. Пример: "jdnga7e". УКАЗЫВАЕМ В КАВЫЧКАХ ОБЯЗАТЕЛЬНО!!!
![Скриншот приватные ключи]([https://github.com/Kuba199403/meteora/issues/1#issuecomment-2350120339](https://github.com/Kuba199403/meteora/blob/main/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202024-09-13%20%D0%B2%2022.31.00.png))
![скриншот2]([https://github.com/Kuba199403/meteora/issues/1#issuecomment-2350120589](https://github.com/Kuba199403/meteora/blob/main/%D0%A1%D0%BD%D0%B8%D0%BC%D0%BE%D0%BA%20%D1%8D%D0%BA%D1%80%D0%B0%D0%BD%D0%B0%202024-09-13%20%D0%B2%2022.49.52.png))
``` python
keyword_wallet = 'qwertyuiop'
```
+ если от кошелька есть пароль разблокировки указываем сюда. УКАЗЫВАЕМ В КАВЫЧКАХ ОБЯЗАТЕЛЬНО!!!

``` python
usdt_swap_value_to_sol: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение
```
+ Количество USDT для обмена на SOl, в дальнейшем для оплаты газа и залога на DLMM. Вами указанная сумма USDT, 
+ после свапа должна сделать минимум 0.08 SOL. 
+ Если оставите значение '0', то у вас на балансе ДОЛЖНО быть 0,08 SOL минимум!!! 
+ Если вы на 'swap_value_to_sol' ничего не укажете, то скрипт будет менять 5 USDT, в случае если баланс опуститься ниже 0.08 SOl.
+ УКАЗЫВАЕМ БЕЗ КАВЫЧЕК!!!

``` python
usdt_swap_value_to_jlp: float = 0  # !!! Нельзя оставлять пустым !!! либо '0', либо ваше значение
```
+ Количество USDT для свапа на JLP, в последующем пойдет для открытия позиции. Если оставите как есть, скрипт будет менять ВСЕ USDT на JLP. 
+ УКАЗЫВАЕМ БЕЗ КАВЫЧЕК!!!

``` python
status_check_interval: int = 60
```
+ Интервал времени на проверку позиции. В каждое определенное вами время будет проверятся состояние позиции. 
+ Надо указать в секундах ОБЬЯЗАТЕЛЬНО!!! УКАЗЫВАЕМ БЕЗ КАВЫЧЕК!!!

``` python
max_procent = '2.75'  # дефолтное значение
```
+ Максимальный процент рейджа. Показаны дефолтное значение
+ ОБЯЗАТЕЛЬНО УКАЗЫВАЕМ В КАВЫЧКАХ !!!
+ 

```python
default_swap_value_for_sol = 5
```
+ Дефолтное значение USDT, используется в случае если количество SOL будет ниже 0.08 (это минимальное значение для работы софта)
+ БЕЗ КАВЫЧЕК ПИШЕМ ЕСЛИ ХОТИМ МЕНЯТЬ ЗНАЧЕНИЕ!!!
```python
params = {
    'token': None,
    'chat_id': None
}
```
+ Указываем Token и chat_id телеграмм бота, если создавали и хотите использовать бота для получения уведомлений в случае прекращения работы софта. 
+ ОБЯЗАТЕЛЬНО УКАЗЫВАЕМ В КАВЫЧКАХ !!!

> **⭐️ Рекомендация**<br>
> Если софт в какой-то момент без явных причин перестанет работать, попробуйте закрыть все позиции вручную и перезапустить софт. 
> В частых случаях из-за слабого интернета сайты могу не загружаться или браузер может не корректно работать. 
> Поэтому прежде чем паниковать или нервничать попробуйте перезапустить софт. Под перезагрузкой подразумевается закрытия всех позиций и вкладок и браузер и закрытия ADSPOWER. 

