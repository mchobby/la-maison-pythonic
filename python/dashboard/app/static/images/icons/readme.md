# Icons ressources
This folder contains the following entries:
* icons/M : Materialize Icons for the select_icon Jinja Macro

# Materialize Icons
The Materialize project [materializecss.com](https://materializecss.com/about.html) includes icons in fonts.

Those icons can easily been included within various parts of the design thank to the `<i class="material-icons">add</i>` markup. That's great!

Unfortunately, those icons cannot been integrated within the materialize <select> item (see [materializecss.com/select.html](https://materializecss.com/select.html) for more info). As a consequence no way to display the icons into a drop down list EXCEPT as a ressource image.

So here is a small subset of icons under png format.

## License notice 

Icons comes form the [material.io](https://material.io) project and release under Apache 2.0 license

See [https://www.apache.org/licenses/LICENSE-2.0.html](https://www.apache.org/licenses/LICENSE-2.0.html)

## Add new icons

Wants to add icons to your collection ?

Lets browse the following link and select an icon:
* [https://material.io/tools/icons/?icon=accessibility&style=twotone](https://material.io/tools/icons/?icon=accessibility&style=twotone)

Then download the icon from the material.io with the following caracteristics:
* 48dp 
* png format.

The icon files (png files) must be extracted from the archive.

Select the pnf file from the archive's "x1" subfolder.

Rename the file once downloaded to the images/icons/M/ folder (M for Materialize).
Keep the shorten par of the image name like shown here under. 

* twotone_accessibility_black_48dp.png --> accessibility.png

## Expand SELECT list

Browse the /templates/macro/M_input.macro and expand the definition as needed for select_icon macro (and other related macro).
