

def unordered_list(body):
    return '<ul>{}</ul>'.format(''.join(body))


def list_item(title, body=''):
    return '<li>{}</li>{}'.format(title, body)


def link(title, link):
    return '<a href="{}">{}</a>'.format(link, title)


def make_page(msg):
    return """
        <!doctype html>
        <html lang="en">
            <head> 
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
                <style>
                p {{
                    margin: 0 0 0 0;
                }}
                </style>
            </head>
            <body class="bg-dark text-white">
                <div class="container">
                    <h1><a href='/'>Bench Explorer</a></h1>
                {}
                </div>
                <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
                <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
                <script>
                    $(function () {{
                      $('[data-toggle="tooltip"]').tooltip()
                    }})
                </script>
            </body>
        </html>
    """.format(msg)