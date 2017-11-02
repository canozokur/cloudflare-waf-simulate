import os
import json
import configparser
import CloudFlare

config = configparser.ConfigParser()
config.read('simulate.cfg')

ZONE_ID = os.environ.get('ZONE_ID') or config.get('simulate', 'zone_id')
WAF_ID = os.environ.get('WAF_ID') or config.get('simulate', 'waf_id')

def main():
    cf = CloudFlare.CloudFlare(raw=True)
    # page_number = 2
    # waf_rules = cf.zones.firewall.waf.packages.rules.get(
    #             ZONE_ID,
    #             WAF_ID,
    #             params={'per_page':5,'page':page_number}
    #             )
    # print(json.dumps(waf_rules, indent=2))

    page_number = 0
    while True:
        page_number += 1
        try:
            waf_rules = cf.zones.firewall.waf.packages.rules.get(
                ZONE_ID,
                WAF_ID,
                params={'per_page':5,'page':page_number})
        except CloudFlare.exceptions.CloudFlareAPIError as e:
            exit('%d %s - api call failed' % (e, e))

        total_pages = waf_rules['result_info']['total_pages']

        for rule in waf_rules['result']:
            if 'simulate' not in rule['allowed_modes']:
                continue

            if rule['mode'] == 'simulate':
                continue

            _data = {'mode': 'simulate'}
            _id = rule['id']
            _description = rule['description']
            _current_mode = rule['mode']
            _default_mode = rule['default_mode']
            print('Simulate mode is available, changing {} to simulate mode'.format(_id))
            try:
                cf.zones.firewall.waf.packages.rules.patch(ZONE_ID, WAF_ID, _id, data=_data)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                print('Error: RuleID {}: {}'.format(_id, e))
                print(json.dumps(rule, indent=4))

        if page_number == total_pages:
            break

if __name__ == '__main__':
    main()
