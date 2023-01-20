# Absorption

An arduino spectrometer was built to obtain the absorption spectrum of an arbitrary sample dissolved in distilled water and also predict the concentration of a sample based on its spectrum.

## Basic principles
### Spectrum
With an RGB LED the sample is illuminated $I_o$ with the 7 main colors of the visible spectrum. On the other side of the sample is a photoresistor to measure the intensity of the output light $I_f$.
![image](https://user-images.githubusercontent.com/121773519/213818269-e4f29044-7ece-4842-89ae-1c89907f5d7b.png)

The absorption is then computed for each color via  $$A=\log_{10}\left(\frac{I_o}{I_f}\right)$$

### Caracterization
However it should be noted that the photoresistor measures voltage and it depends on the wavelenght (color) of the light source. So in order to translate what the photoresistor measures (Voltage) and the actual physical quantity (Intensity) a caracterization was employed.
For this there were two stages:
- The intensity of the RGB LED was varied from the minimum capacity to the maximum and the voltage data was gathered.
- The previous step was repeated but changing the photoresistor with a smartphone in order to measure the light intensity with the Phyphox app.
Finally both datasets were associated along the time axis for each color to fit the intensity data vs the voltage data.

### Prediction
With some spectrums associated with known concentrations for a given substance, it is fitted a linear regression model (because of Beer-Lambert's law) for each color.
Then for an unkown concentration its spectrum is computed and the result is evaluated for each one of the 7 models. Finally the predictions are displayed along with the average.

## Circuit diagram
![image](https://user-images.githubusercontent.com/121773519/213814558-a668fa34-6c39-4e73-aa74-ace89dc08007.png)
Credit: Ana Caviedes, avcaviedesa@unal.edu.co

# Results 
## Caracterization
### Intensity vs voltage polynomial fit (degree 3)
![image](https://user-images.githubusercontent.com/121773519/213814992-5253c370-8975-4e7c-a0ae-fb25e18eb19d.png)

## Spectrum example
![image](https://user-images.githubusercontent.com/121773519/213816221-bac19f93-ce30-4cd6-b893-17b4d34d5a28.png)

## Concentration predictions
![image](https://user-images.githubusercontent.com/121773519/213816659-a1e44e53-071b-4df4-b431-a96c75d00554.png)
The real concentration was 0.65 [mol/L] this gives a 12% error with respect to the mean prediction and a minimun error of 3% provided by the red prediction (the same one that presented maximum absorption)
