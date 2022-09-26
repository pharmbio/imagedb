# Merge image directories (Usually because interrupted IMX session)

1. Move overlapping images from destination folder to "Trash" folder
   On QNAP:
   `mkdir -p /share/mikro/IMX/MDC_pharmbio/trash/<project>/<plate>`
   `mv /share/mikro/IMX/MDC_pharmbio/project/wildcard-can-be-used /share/mikro/IMX/MDC_pharmbio/trash/`

2. Delete overlapping images from database
   `DELETE FROM images WHERE plate_acquisition_id = <acc_id> AND well = <well>`

3. Move files from source folder tp destination
   `DELETE FROM images WHERE plate_acquisition_id = <acc_id> AND well = <well>`

4. Set finished column to NULL in database in table plate_acquisition
   `UPDATE plate_acquisition SET finished = NULL WHERE plate_acquisition_id = <acc_id>`

5. Delete source images from db and file

