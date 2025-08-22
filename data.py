from datetime import datetime
from scraper import movie_img_link, movies_title
import random


sports_images = [
    "https://t3.ftcdn.net/jpg/02/87/04/00/360_F_287040077_U2ckmhpzeyqDHiybj0dfCfX6NRCEKdoe.jpg",
    "https://media.istockphoto.com/id/1355687160/photo/various-sport-equipment-gear.jpg?s=612x612&w=0&k=20&c=NMA7dXMtGLJAin0z6N2uqrnwLXCRCXSw306SYfS49nI=",
    "https://media.istockphoto.com/id/949190756/photo/various-sport-equipments-on-grass.jpg?s=612x612&w=0&k=20&c=s0Lz_k0Vq_9P6JBETBMtLsK0lSKEHg4Tnqz9KlRCSHA=",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGd2iLHbzyC9PLp1Gwk0mr0_WctRwLLYcQHw&s"

]

indian_images = [
    "https://variety.com/wp-content/uploads/2024/10/India-Reality-TV-collage.jpg?w=1000&h=667&crop=1",
    "https://assets.change.org/photos/6/af/dm/iyafdmxPvTzpgsK-1600x900-noPad.jpg?1528917136",
    "https://img.jagranjosh.com/images/2022/October/14102022/highest-grossing-films.jpg",
    "https://i.redd.it/29mxikce92fe1.png",
    "https://www.quertime.com/wp-content/uploads/2018/12/best-websites-to-watch-free-bollywood-hindi-movies.jpg"
]


#bg images

BG_IMAGES = [
    "https://e1.pxfuel.com/desktop-wallpaper/158/418/desktop-wallpaper-movieverse-2022-bollywood-hollywood-movies-in-dual-audio-hollywood-2022-movies-poster.jpg",

    "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?fm=jpg&q=60&w=3000&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MTJ8fG1vdmllfGVufDB8fDB8fHww",

    "https://c8.alamy.com/comp/M70A61/collection-of-american-movies-films-on-dvd-showing-movie-stars-film-M70A61.jpg",

    "https://i.ytimg.com/vi/qtl1jVevIVo/maxresdefault.jpg"
]


# Product Data
PRODUCTS = [
            {
        "id": 1,
        "name": "GMA X1 Pro",
        "price": 299.99,
        "badge": "GMA TV 10.0 & 10.1",
        "desc1": "Material: Plastic",
        "desc2": "Wifi: 2.4G/5GHZ",
        "desc3": "CPU: RK3328 QUAD-CORE 64BIT CT-A53\n, RAM: 8GB\n, ROM: 128GB/512GB\nBT: 4.0\n",
        "rating": "4.9 ⭐⭐⭐⭐⭐",
        "shipping": "3-5 days max.",
        "image": [
            "/static/img/p6.png"
        ],

        # "Product Uses Instructions": ">open the box from the package.\n>plug the power charger.\n>plug the HD cable.\n>plug the Lan cable if needed.\n>connect the TV box with your BIG TV.\n>wait for opening."
    },

    {
        "id": 2,
        "name": "GMA X2",
        "price": 249.99,
        "badge": "GMA TV 9.0 & 9.1",
        "desc1": "Material: Plastic",
        "desc2": "Wifi: 2.4G/5GHZ",
        "desc3": "CPU: RK3328 QUAD-CORE 64BIT CT-A53\n, RAM: 2GB (2GB OPTION)\n, ROM: 16GB/32GB\nBT: 4.0\n",
        "rating": "4.5 ⭐⭐⭐⭐",
        "shipping": "3-5 days max.",
        "image": [
            "/static/img/p2.png",
            "/static/img/p21.png",
            "/static/img/p22.png",
            "/static/img/p23.png"
        ],

        # "Product Uses Instructions": ">open the box from the package.\n>plug the power charger.\n>plug the HD cable.\n>plug the Lan cable if needed.\n>connect the TV box with your BIG TV.\n>wait for opening."
    },
    {
        "id": 3,
        "name": "GMA X3",
        "price": 199.99,
        "badge": "Amlogic S905X3",
        "desc1": "PROCESSOR : G31 TM MP2 GPU, 64-bit quad core ARM Cortex A55 CPU",
        "desc2": "PACKAGE: EMMC 32GB (16GB/64GB OPTION), FLASH: DDR3 4GB (2GB OPTION)",
        "desc3": "OS: V9.0 ( 10.0 OPTION), BT: 4.0 /4.1, WIFI: 2.4/5.8G 1000MBPS",
        "rating": "4.4 ⭐⭐⭐⭐",
        "shipping": "3-5 days max.",
        "image": [
            "/static/img/p1.png",
            "/static/img/p11.png"
        ],
        
        # "PUI": ">open the box from package.\n>plug the power charger.\n>plug the HD cable.\n>plug the Lan cable if needed.\n>connect the TV box with your BIG TV.\n>waiting for opening."
    },

    {
        "id": 4,
        "name": "Air Remote",
        "price": 29.99,
        "badge": "Wireless Keyboard W1",
        "desc1": "WeChip 2.4G for Android TV Box/PC/Projector/HTPC/All-in-one PC and More, Brand: VIAXOS",
        "desc2":"Manufacturer: WECHIP",
        "desc3": "Item part number: V3473",
        "rating": "4.6 ⭐⭐⭐⭐⭐",
        "shipping": "3-5 days max.",
        "image": [
        "/static/img/p30.png",
        "/static/img/p31.png",
        "/static/img/p32.png",
        "/static/img/p34.png",
        ]
    },

    {
        "id": 5,
        "name": "Air Remote Pro",
        "price": 39.99,
        "badge": "Wireless Keyboard Mouse",
        "desc1": "Voice Input Android TV Remote Control Infrared Leaning for Android TV Box,Mini PC,Mac OS.",
        "desc2": "Brand: X96\nManufacturer: Sree Info Enterprises\nProduct Dimensions: 15 x 4 x 2 cm; 100 Grams\nItem part number: SreeTeK™ 001\nRAM Size: 128 MB\nHard Drive Size: 1 MB\nProcessor Speed: 1.2 GHz\nHardware Interface: USB, USB 1.1, USB 2.0\nCompatible Devices: Laptop, Television, Set Top Box, Streaming Players, Computer\nMounting Hardware: 1 x Air Mouse, 1 x USB Receiver",
        "desc3": "Battery Description: AAA\n""Batteries Included : No \n Batteries Required :No\nTotal Usb Ports: 1\nConnector Type : Infrared\nDevice interface - primary : Mouse, Keyboard",
        "rating": "4.2 ⭐⭐⭐⭐",
        "shipping": "3-5 days max.",
        "image": [
            "/static/img/p4.png",
            "/static/img/p42.png"
        ]
    },
    {
        "id": 6,
        "name": "4 in 1 Air Remote",
        "price": 49.99,
        "badge": "Voice Remote Control",
        "desc1": "Wireless Keyboard Touchpad, Anti-Lost Function, for Nvidia Shield, Android TV Box, PC.",
        "desc2": "Brand: ZYF\n, Product Dimensions: 19.05 x 5.33 x 1.02 cm; 108.86 Grams\n, Batteries: 1 Lithium ion batteries required. (included, rechargeable).\nItem model number: Z10-W\nCompatible Devices: Projector, Television, Digital Camera, Streaming Players, Computer, Tablet, Home Theater",
        "desc3": "Connector Type: Radio Frequency\nItem Weight: 109 g",
        "rating": "4.8 ⭐⭐⭐⭐⭐",
        "shipping": "3-5 days max",
        "image": [
            "/static/img/p50.png",
            "/static/img/p5.png",
            "/static/img/p51.png",
            "/static/img/p501.png"
        ]
    },

]





PLANS = [
    {
        "id": 1,
        "title": "Monthly Plan",
        "price": 29.99,
        "period": "month",
        "features": ["Basic Live TV Channels", "VOD Facilities", "Standard Support"],
        "cta": "Start Free Trial"
    },
    {
        "id": 2,
        "title": "Half Yearly Plan",
        "price": 99.99,
        "period": "six months",
        "features": ["Basic Live TV Channels", "VOD Facilities", "24/7 Support with monthly updates"],
        "cta": "Start Free Trial"
    },
    {
        "id": 3,
        "title": "Basic Plan",
        "price": 199.99,
        "period": "year",
        "features": ["100+ Countries Live TV Channels", "VOD Facilities (OTT Platform Content)", "Series access", "24/7 Support with monthly updates"],
        "cta": "Start 24h Trial"
    },
    {
        "id": 4,
        "title": "Plus Plan",
        "price": 299.99,
        "period": "3 year",
        "features": ["Everything in Basic", "Tons of Movies", " Catch-Up Programs", "24/7 Support", "Weekly Updates"],
        "cta": "Go Plus with Free Trial"
    },
    {
        "id": 5,
        "title": "Pro Plan",
        "price": 399.99,
        "period": "5 year",
        "features": ["Everything in Plus", "Local & Regional Channels", "Pause & Play Service Facility", "Priority Support", "Daily Updates"],
        "cta": "Go Pro with Free Trial"
    },
    {
        "id": 6,
        "title": "Ultimate Plan",
        "price": 499.99,
        "period": "Lifetime",
        "features": ["Everything in Pro", "Exclusive Content", "Offline Viewing", "Family Sharing", "Priority Customer Support"],
        "cta": "Go Ultimate with Free Trial"
    }
]




CHANNEL_GROUPS = [
    {
        "title": "All Sports Channels",
        "icon": "🏆",
        "image": random.choice(sports_images)
    },
    {
        "title": "All Hindi and Punjabi Channels",
        "icon": "🪔",
        "image": random.choice(indian_images)
    },
    {
        "title": "All English, Spanish, Arabic and African Channels",
        "icon": "⚽︎",
        "image": "https://i.pinimg.com/564x/15/53/ce/1553ce653eb0b74e9d3e821fece704d3.jpg"
    },
    {
        "title": "All Online Cinema In All devices",
        "icon": "🎦",
        "image": "https://images.gizbot.com/img/2021/02/what-is-ott-platform-best-10-ott-platforms-in-india-1613237548.jpg"
    },
    {
        "title": "All Latest Shows",
        "icon": "🎞️",
        "image": "https://indiaobservers.com/wp-content/uploads/2022/07/top-web-series-in-the-world-highest-rated.jpg"
    },
    {
        "title": "All Your Favourite TV in One Place",
        "icon": "📺",
        "image": "https://media.istockphoto.com/id/481950235/video/journey-through-a-video-wall-ending-on-a-green-screen.jpg?s=640x640&k=20&c=19pj7xiONZ-IPWOYYtzwPSTQXOKtOhbudWMJqLhIxPk="
    },
]




POSTS = [
    {"slug": "welcome-to-globe", "title": "Welcome to the New GlobeMTV", "excerpt": "A faster, simpler way to stream what you love.", "date": datetime(2025, 8, 1)},

    {"slug": "what-is-GMTV", "title": "What is GMTV ?", "excerpt": "GMTV uses Internet technology to send television programming to your TV. GMTV uses a broadband Internet connection for top international programming directly to your home without a satellite dish. Just connect your receiver to your GMTV Internet from the house and on your TV, then sit back and enjoy.", "date": datetime(2025, 8, 10)},

    {"slug": "enjoy-watching-latest-shows", "title": "Enjoy watching the latest Shows and classic movies from GlobeMTV", "excerpt": "LIVE GMTV is an online streaming worldwide GMTV subscription service provider with fast activation and no setup fees. covering all your day-to-day devices. Our team supplies solid GMTV services to various countries. And our network engineers deliver high-quality digital media streaming to our loyal customers. Our strong support team and technical expertise have allowed us to be the best GMTV service provider available worldwide.", "date": datetime(2025, 8, 15)},

    {"slug": "24h-free-trial", "title": "Get a 24 hour Free Trial", "excerpt": "The offers are purely based on customization which helps our customers to pay only for what they get. We are pleased to announce that if you discontinue our service for a period and pre inform us then the services will be continued for that period further without paying any extra amount if you resume it. However, if you are keen to invest in any of our prime offerings, you are gonna have the best TV experience ever.", "date": datetime(2025, 8, 20)}
]


MOVIES = [
    {
        "title": movies_title[i],
        "image": movie_img_link[i]
    }
    for i in range(len(movies_title))
]

msg="Subject: About GlobeMTV IPTV\n\n"
msg+="\nLIVE GMTV is an online streaming worldwide GMTV subscription service provider with fast activation and no setup fees, covering all your day-to-day devices."
msg+= "\nOur team supplies solid GMTV services to various countries. And our network engineers deliver high-quality digital media streaming to our loyal customers. Our strong support team and technical expertise have allowed us to be the best GMTV service provider available worldwide.\n"
msg+="\nOur company provides GMTV subscription services straight to your device through the internet. This includes Smart TV Samsung & LG, PC, Mac, Apple iPhone, iPad, Apple TV 4 & 5, Amazon Fire Stick, GMTV box, Android phones, and tablets, Android box, MAG, AVOV, VU+, Enigma 2, Dreambox, Openbox, Dreamlink and STB Emulator.\n"
msg+="\nWe give customers direct exclusive access to 12,000+ Live standard and 4k Ultra HD channels and 35,000+ VOD, ranging from sports, movies, 18+ and popular TV shows. Stream your favorite channels straight from your home."


COUPONS = [
    {
        "code": "WELCOME4",
        "discount": 4.99,
        "description": "Get 4.99$ off on all subscriptions"
    },
    {
        "code": "WELCOME9",
        "discount": 9.99,
        "description": "Get 9.99$ off on all subscriptions"
    },
    {
        "code": "WELCOME19",
        "discount": 19.99,
        "description": "Get 19.99$ off on all subscriptions"
    },
    {
        "code": "WELCOME29",
        "discount": 29.00,
        "description": "Get 29.00$ off on your first subscription"
    },
    {
        "code": "WELCOME49",
        "discount": 49.99,
        "description": "Get 49.99$ off on your first subscription"
    },
    {
        "code": "WELCOME69",
        "discount": 69.99,
        "description": "Get 69.99$ off on your first subscription"
    },
    {
        "code": "WELCOME99",
        "discount": 99.99,
        "description": "Get 99.99$ off on your first subscription"
    }
]




