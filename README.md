# xmltree2xml

[![build](https://github.com/remigermain/xmltree2xml/actions/workflows/main.yml/badge.svg)](https://github.com/remigermain/xmltree2xml/actions/workflows/main.yml)
[![pypi](https://img.shields.io/pypi/v/xmltree2xml)](https://pypi.org/project/xmltree2xml/)

xmltree2xml convert a compile xmltree from android to classic xml

# Usage

```
usage: xmltree2xml [-h] [-n NO_HEADER] [-o OUTPUT_DIR] file [file ...]

convert android xmltree to classic xml.

positional arguments:
  file                  xmltree file

options:
  -h, --help            show this help message and exit
  -n NO_HEADER, --no-header NO_HEADER
                        do not add an xml header.
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        output directory.
```

## Input file syntax

the android xml compile look like this

```
E: list (line=16)
  A: name="carrier_config_list" (Raw: "carrier_config_list")
    E: pbundle_as_map (line=17)
        E: string-array (line=19)
          A: name="mccmnc" (Raw: "mccmnc")
            E: item (line=20)
              A: value="TEST" (Raw: "TEST")
    E: pbundle_as_map (line=24)
        E: string-array (line=26)
          A: name="mccmnc" (Raw: "mccmnc")
            E: item (line=28)
              A: value=20601
            E: item (line=30)
              A: value=20810
            E: item (line=31)
              A: value=20826
        E: string (line=33)
          A: name="feature_flag_name" (Raw: "feature_flag_name")
            T: 'vvm_carrier_flag_el_telecom'
        E: int (line=34)
          A: name="vvm_port_number_int" (Raw: "vvm_port_number_int")
          A: value=5499
        E: string (line=37)
          A: name="vvm_destination_number_string" (Raw: "vvm_destination_number_string")
            T: '8860'
        E: string (line=38)
          A: name="vvm_type_string" (Raw: "vvm_type_string")
            T: 'vvm_type_omtp_1_3'
    E: pbundle_as_map (line=41)
        E: string-array (line=43)
          A: name="mccmnc" (Raw: "mccmnc")
```

and output look like this

```xml
<?xml version="1.0" encoding="utf-8"?>
<list name="carrier_config_list">
    <pbundle_as_map>
        <string-array name="mccmnc">
            <item value="TEST" />
        </string-array>
    </pbundle_as_map>
    <pbundle_as_map>
        <string-array name="mccmnc">
            <item value="20601" />
            <item value="20810" />
            <item value="20826" />
        </string-array>
        <string name="feature_flag_name">vvm_carrier_flag_el_telecom</string>
        <int name="vvm_port_number_int" value="5499" />
        <string name="vvm_destination_number_string">8860</string>
        <string name="vvm_type_string">vvm_type_omtp_1_3</string>
    </pbundle_as_map>
    <pbundle_as_map>
        <string-array name="mccmnc" />
    </pbundle_as_map>
</list>
```

## License

[MIT](https://github.com/remigermain/xmltree2xml/blob/main/LICENSE)
