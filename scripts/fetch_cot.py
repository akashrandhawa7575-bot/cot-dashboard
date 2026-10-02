#!/usr/bin/env python3
"""Fetch CFTC COT data (Legacy + Disaggregated) and write data/cot.json.
Same markets / limit (260 weeks) as the dashboard, so the page can load the
snapshot instead of hitting CORS proxies from the browser."""
import json, sys, time, urllib.parse, urllib.request

LEGACY = 'https://publicreporting.cftc.gov/resource/6dca-aqww.json'
DISAGG = 'https://publicreporting.cftc.gov/resource/kh3c-gbw2.json'

LEGACY_MARKETS = {
 'EUR':'EURO FX - CHICAGO MERCANTILE EXCHANGE',
 'GBP':'BRITISH POUND STERLING - CHICAGO MERCANTILE EXCHANGE',
 'JPY':'JAPANESE YEN - CHICAGO MERCANTILE EXCHANGE',
 'CHF':'SWISS FRANC - CHICAGO MERCANTILE EXCHANGE',
 'CAD':'CANADIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
 'AUD':'AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE',
 'NZD':'NEW ZEALAND DOLLAR - CHICAGO MERCANTILE EXCHANGE',
 'MXN':'MEXICAN PESO - CHICAGO MERCANTILE EXCHANGE',
 'GOLD':'GOLD - COMMODITY EXCHANGE INC.',
 'SILVER':'SILVER - COMMODITY EXCHANGE INC.',
 'COPPER':'COPPER- #1 - COMMODITY EXCHANGE INC.',
 'PLATINUM':'PLATINUM - NEW YORK MERCANTILE EXCHANGE',
 'PALLADIUM':'PALLADIUM - NEW YORK MERCANTILE EXCHANGE',
}
DISAGG_IDS = ['EUR','GBP','JPY','CHF','CAD','AUD','NZD','GOLD','SILVER','COPPER']

def get(base, name, tries=4):
    q = ("?$where=market_and_exchange_names=%27" + urllib.parse.quote(name) +
         "%27&$order=report_date_as_yyyy_mm_dd%20DESC&$limit=260")
    for i in range(tries):
        try:
            with urllib.request.urlopen(base + q, timeout=60) as r:
                rows = json.load(r)
            if rows: return rows
        except Exception as e:
            print(f'  retry {i+1} {name}: {e}', file=sys.stderr)
        time.sleep(3 * (i + 1))
    return None

def main():
    out = {'legacy': {}, 'disagg': {}}
    for mid, name in LEGACY_MARKETS.items():
        rows = get(LEGACY, name)
        if rows: out['legacy'][mid] = rows
        else: print(f'FAILED legacy {mid}', file=sys.stderr)
    for mid in DISAGG_IDS:
        rows = get(DISAGG, LEGACY_MARKETS[mid])
        if rows: out['disagg'][mid] = rows
        else: print(f'FAILED disagg {mid}', file=sys.stderr)
    # refuse to overwrite a good snapshot with a badly incomplete one
    if len(out['legacy']) < len(LEGACY_MARKETS) - 2:
        sys.exit('Too many legacy markets failed; keeping previous snapshot.')
    with open('data/cot.json', 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    d = next(iter(out['legacy'].values()))[0]['report_date_as_yyyy_mm_dd']
    print(f"OK: {len(out['legacy'])} legacy, {len(out['disagg'])} disagg, latest report {d}")

if __name__ == '__main__': main()
