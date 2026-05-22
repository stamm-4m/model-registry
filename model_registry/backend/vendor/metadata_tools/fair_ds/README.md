# metadata_tools



## FAIR-Data Station

The `fairds_ontology.py` file is for the metadata ontology files for the FAIR Data Station (FAIR-DS)


### Notes: 'Item label'

The class `fairds_ontology` can produce sets and dictionaries with the terms ('Item labels') and the units used in FAIR data stations ontology please
note that the keys are forced to be lower case (`.lower()`) to ensure that the keys are comparable.


## Example code

### Example: Set terms for each level

Take the terms and apply them to the various hierarchical levels

``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()    

#-------------------
# to show the change print out the first 100 rows...
print(fds.observationunit.head(100))

#-------------------
# ... then set the terms...
fds.set_terms()

#-------------------
# ... and now lets see the change.
print(fds.observationunit.head(100))

#-------------------
# Now save the excel this makes a '..._tmp.xlsx' file
fds.save_excel()

```


### Example: Load excel file
``` python

fds = fairds_ontology()
fds.load_from_excel()


```             
        

### Example: Convert excel file to tsv
``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.convert_to_tsv()


```           
        

### Example: Load from tsv files
``` python

fds = fairds_ontology()
fds.load_from_tsv()
fds.pretty_print(fds.terms)
print(fds.terms['Preferred unit'])


``` 

### Example: Terms to dict

Put all the ontological terms into a dictionary and set as well as the units into a dictionary and set


``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()

```

### Example: Terms to dict

``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()
print(fds.terms_all)
        
```

### Example: Get units

Print out the set of units

``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()     
print(fds.terms_units)

```        

### Example: Get a term

Print out a single term

``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()     
print(fds.terms['Item label'])

```        

### Example: Get a unit

Print out units

``` python

fds = fairds_ontology()
fds.load_from_excel()
fds.get_all_terms()     
print(fds.terms_units_dict)

print('\n\n')
print(fds.terms_units_dict.keys())
            
print('\n\n')
print(fds.terms_units_dict['ºC'])

print('\n\n')  
fds.query_term_units(query_='%')

```         

### Example: Get level

Print out the first 100 rows of a particular hierarchical level


``` python

fds = fairds_ontology()
fds.load_from_excel()
print(fds.observationunit.head(100))

```        


