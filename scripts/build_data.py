#!/usr/bin/env python3
"""Validate the per-scale data tree. This command no longer generates data.json."""
from clinical_data import load_clinical_data, validate_data

def main():
    data = load_clinical_data()
    validate_data(data)
    print('Valid modular data:', len(data['domains']), 'domains,', len(data['scales']), 'table scales')

if __name__ == '__main__':
    main()
