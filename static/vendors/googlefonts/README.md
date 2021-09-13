extract css file from google url:
- https://fonts.googleapis.com/css?family=Open+Sans:300,400,600,700
- https://fonts.googleapis.com/css?family=Roboto:400,300,500,700

use this js command to print all urls:

```javascript
document.body.innerText.match(/(https:\/\/[\w./-]+)/mg)
``` 

copy the out put into a file and use `wget -i <file name>` to download all fonts files

replace url with font file path

use the css files instead of google fonts css