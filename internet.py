#!/usr/bin/env python
#

def download(package, platform, distribution, architecture):
    def _get_url(package, platform, distribution, architecture):
        # TODO : Move this to a config file somewhere else
        references = {
            ('rez-nuke', 'Linux', 'x86_64'): 'https://www.foundry.com/products/download_product?file=Nuke11.2v3-linux-x86-release-64.tgz',
        }

        options = [
            (package, platform, distribution, architecture),
            (package, platform, architecture),
        ]

        for option in options:
            try:
                url = references[option]
            except KeyError:
                continue

            if common.is_url_reachable(url):
                return url

        return ''

    def _install_from_url(url):
        raise NotImplementedError('Need to write this.')

    url = _get_url(package, platform, distribution, architecture)

    if not url:
        raise RuntimeError('No URL could be found for "{data}".'.format(
            data=(package, platform, distribution, architecture)))

    _install_from_url(url)
