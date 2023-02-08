# Västblekinge Miljö AB Sophämtning

Support for schedules provided by [Västblekinge Miljö AB](https://cal.vmab.se), serving the western part of Blekinge, Sweden.

Note that they only provide their calendar service for customers with the "Fyrfack" bins which means this will only work for regular residential houses and not for apartment buildings, city services locations or similar.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
  sources:
    - name: vmab_se
      args:
        street_address: STREET_ADDRESS
```

### Configuration Variables

**street_address**  
*(string) (required)*

## Example

```yaml
waste_collection_schedule:
  sources:
    - name: vmab_se
      args:
        street_address: Parkvägen 11, Mörrum
```

## How to get the source argument

The source argument is the address to the house with waste collection. The address can be tested [here](https://cal.vmab.se).

## Types returned

The following waste types will be returned:

* "Max 1, Fyrfackskärl"

* "Max 2, Fyrfackskärl"
