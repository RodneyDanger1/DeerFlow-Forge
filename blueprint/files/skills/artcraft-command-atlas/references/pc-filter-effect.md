# PhotoCraft Filter Effect

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **131** across 2 groups.

## Coverage

`filter` 124 · `style` 7

## `filter` (124)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `filter.adaptiveWideAngle` | Adaptive Wide Angle… | Filter | {"model":"auto\|fisheye\|perspective\|fullSpherical","focalLength":0..200=0,"cropFactor":0.1..10=1,"scale":50..150=100,"constraints":[{"a":[x,y],"b":[x,y],"orientation":"free\|horizontal\|vertic… | needs document; disabled in catalogue snapshot |
| `filter.blur.average` | Average | Filter > Blur | {} | needs document; disabled in catalogue snapshot |
| `filter.blur.blur` | Blur | Filter > Blur | {} | needs document; disabled in catalogue snapshot |
| `filter.blur.blurMore` | Blur More | Filter > Blur | {} | needs document; disabled in catalogue snapshot |
| `filter.blur.boxBlur` | Box Blur… | Filter > Blur | {"radius":1..2000=1} | needs document; disabled in catalogue snapshot |
| `filter.blur.gaussianBlur` | Gaussian Blur… | Filter > Blur | {"radius":0.1..1000=1} | needs document; disabled in catalogue snapshot |
| `filter.blur.lensBlur` | Lens Blur… | Filter > Blur | {"radius":0..100=15,"shape":"hexagon\|triangle\|square\|pentagon\|heptagon\|octagon","bladeCurvature":0..100=0,"rotation":0..360=0,"depthMap":"none\|transparency\|layerMask\|channel","depthChannel"… | needs document; disabled in catalogue snapshot |
| `filter.blur.motionBlur` | Motion Blur… | Filter > Blur | {"angle":-360..360=0,"distance":1..2000=10} | needs document; disabled in catalogue snapshot |
| `filter.blur.radialBlur` | Radial Blur… | Filter > Blur | {"amount":1..100=10,"method":"spin\|zoom","quality":"draft\|good\|best"="good","centerX":0..1=0.5,"centerY":0..1=0.5} | needs document; disabled in catalogue snapshot |
| `filter.blur.shapeBlur` | Shape Blur… | Filter > Blur | {"radius":5..1000=10,"shape":"circle\|ring\|square\|diamond\|triangle\|hexagon\|star\|heart\|cross"} | needs document; disabled in catalogue snapshot |
| `filter.blur.smartBlur` | Smart Blur… | Filter > Blur | {"radius":0.1..100=3,"threshold":0.1..100=25,"quality":"high\|medium\|low","mode":"normal\|edgeOnly\|overlayEdge"} | needs document; disabled in catalogue snapshot |
| `filter.blur.surfaceBlur` | Surface Blur… | Filter > Blur | {"radius":1..100=5,"threshold":2..255=15} | needs document; disabled in catalogue snapshot |
| `filter.blurGallery.fieldBlur` | Field Blur… | Filter > Blur Gallery | {"blur":0..500=15,"centerX":0..1=0.5,"centerY":0..1=0.5,"pins":json} | needs document; disabled in catalogue snapshot |
| `filter.blurGallery.irisBlur` | Iris Blur… | Filter > Blur Gallery | {"blur":0..500=15,"centerX":0..1=0.5,"centerY":0..1=0.5,"radiusX":0.01..1=0.35,"radiusY":0.01..1=0.25,"angle":-180..180=0,"roundness":0..100=0,"feather":0..0.99=0.5,"pins":json} | needs document; disabled in catalogue snapshot |
| `filter.blurGallery.pathBlur` | Path Blur… | Filter > Blur Gallery | {"speed":0..500=50,"taper":0..100=0,"startX":0..1=0.2,"startY":0..1=0.5,"endX":0..1=0.8,"endY":0..1=0.5,"paths":json} | needs document; disabled in catalogue snapshot |
| `filter.blurGallery.spinBlur` | Spin Blur… | Filter > Blur Gallery | {"blurAngle":0..360=15,"centerX":0..1=0.5,"centerY":0..1=0.5,"radiusX":0.01..1=0.3,"radiusY":0.01..1=0.3,"angle":-180..180=0,"pins":json} | needs document; disabled in catalogue snapshot |
| `filter.blurGallery.tiltShift` | Tilt-Shift… | Filter > Blur Gallery | {"blur":0..500=15,"centerX":0..1=0.5,"centerY":0..1=0.5,"angle":-90..90=0,"focus":0..1=0.1,"transition":0.01..1=0.15} | needs document; disabled in catalogue snapshot |
| `filter.cameraRaw` | Camera Raw Filter… | Filter | {"temperature":-100..100=0,"tint":-100..100=0,"exposure":-5..5=0,"contrast":-100..100=0,"highlights":-100..100=0,"shadows":-100..100=0,"whites":-100..100=0,"blacks":-100..100=0,"texture":-1… | needs document; disabled in catalogue snapshot |
| `filter.convertForSmartFilters` | Convert for Smart Filters | Filter | {"layer":id?} (default: combine selected layers) | needs document; disabled in catalogue snapshot |
| `filter.distort.displace` | Displace… | Filter > Distort | {"horizontal":-999..999=10,"vertical":-999..999=10,"fit":"stretch\|tile","undefinedAreas":"repeat\|wrap","mapDocument":doc,"mapPath":text,"mapLayer":json} | needs document; disabled in catalogue snapshot |
| `filter.distort.pinch` | Pinch… | Filter > Distort | {"amount":-100..100=50} | needs document; disabled in catalogue snapshot |
| `filter.distort.polarCoordinates` | Polar Coordinates… | Filter > Distort | {"mode":"rectangularToPolar\|polarToRectangular"} | needs document; disabled in catalogue snapshot |
| `filter.distort.ripple` | Ripple… | Filter > Distort | {"amount":-999..999=100,"size":"small\|medium\|large"} | needs document; disabled in catalogue snapshot |
| `filter.distort.shear` | Shear… | Filter > Distort | {"amount":-100..100=0,"undefinedAreas":"wrap\|repeat","points":json} | needs document; disabled in catalogue snapshot |
| `filter.distort.spherize` | Spherize… | Filter > Distort | {"amount":-100..100=100,"mode":"normal\|horizontalOnly\|verticalOnly"} | needs document; disabled in catalogue snapshot |
| `filter.distort.twirl` | Twirl… | Filter > Distort | {"angle":-999..999=50} | needs document; disabled in catalogue snapshot |
| `filter.distort.wave` | Wave… | Filter > Distort | {"generators":1..999=5,"wavelengthMin":1..998=10,"wavelengthMax":2..999=120,"amplitudeMin":1..998=5,"amplitudeMax":1..999=35,"type":"sine\|triangle\|square","undefinedAreas":"wrap\|repeat","se… | needs document; disabled in catalogue snapshot |
| `filter.distort.zigZag` | ZigZag… | Filter > Distort | {"amount":-100..100=10,"ridges":0..20=5,"style":"pondRipples\|outFromCenter\|aroundCenter"} | needs document; disabled in catalogue snapshot |
| `filter.filterGallery` | Filter Gallery… | Filter | {"effects":json,"foreground":json,"background":json,"list":bool} | needs document; disabled in catalogue snapshot |
| `filter.gallery.accentedEdges` | Accented Edges |  | {"edgeWidth":1..14=2,"edgeBrightness":0..50=38,"smoothness":1..15=5} | needs document; disabled in catalogue snapshot |
| `filter.gallery.angledStrokes` | Angled Strokes |  | {"directionBalance":0..100=50,"strokeLength":3..50=15,"sharpness":0..10=3} | needs document; disabled in catalogue snapshot |
| `filter.gallery.basRelief` | Bas Relief |  | {"detail":1..15=13,"smoothness":1..15=3,"light":"bottom\|bottomLeft\|left\|topLeft\|top\|topRight\|right\|bottomRight","foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.chalkCharcoal` | Chalk & Charcoal |  | {"charcoalArea":0..20=6,"chalkArea":0..20=6,"strokePressure":0..5=1,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.charcoal` | Charcoal |  | {"charcoalThickness":1..7=1,"detail":0..5=5,"lightDarkBalance":0..100=50,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.chrome` | Chrome |  | {"detail":0..10=4,"smoothness":0..10=7} | needs document; disabled in catalogue snapshot |
| `filter.gallery.coloredPencil` | Colored Pencil |  | {"pencilWidth":1..24=4,"strokePressure":0..15=8,"paperBrightness":0..50=25} | needs document; disabled in catalogue snapshot |
| `filter.gallery.conteCrayon` | Conté Crayon |  | {"foregroundLevel":1..15=11,"backgroundLevel":1..15=7,"texture":"canvas\|brick\|burlap\|sandstone","scaling":50..200=100,"relief":0..50=4,"light":"top\|topRight\|right\|bottomRight\|bottom\|bottomL… | needs document; disabled in catalogue snapshot |
| `filter.gallery.craquelure` | Craquelure |  | {"crackSpacing":2..100=15,"crackDepth":0..10=6,"crackBrightness":0..10=9} | needs document; disabled in catalogue snapshot |
| `filter.gallery.crosshatch` | Crosshatch |  | {"strokeLength":3..50=9,"sharpness":0..20=6,"strength":1..3=1} | needs document; disabled in catalogue snapshot |
| `filter.gallery.cutout` | Cutout |  | {"numberOfLevels":2..8=4,"edgeSimplicity":0..10=4,"edgeFidelity":1..3=2} | needs document; disabled in catalogue snapshot |
| `filter.gallery.darkStrokes` | Dark Strokes |  | {"balance":0..10=5,"blackIntensity":0..10=6,"whiteIntensity":0..10=2} | needs document; disabled in catalogue snapshot |
| `filter.gallery.diffuseGlow` | Diffuse Glow |  | {"graininess":0..10=6,"glowAmount":0..20=10,"clearAmount":0..20=15,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.dryBrush` | Dry Brush |  | {"brushSize":0..10=2,"brushDetail":0..10=8,"texture":1..3=1} | needs document; disabled in catalogue snapshot |
| `filter.gallery.filmGrain` | Film Grain |  | {"grain":0..20=4,"highlightArea":0..20=0,"intensity":0..10=10} | needs document; disabled in catalogue snapshot |
| `filter.gallery.fresco` | Fresco |  | {"brushSize":0..10=2,"brushDetail":0..10=8,"texture":1..3=1} | needs document; disabled in catalogue snapshot |
| `filter.gallery.glass` | Glass |  | {"distortion":0..20=5,"smoothness":1..15=3,"texture":"frosted\|blocks\|canvas\|tinyLens","scaling":50..200=100,"invert":bool} | needs document; disabled in catalogue snapshot |
| `filter.gallery.glowingEdges` | Glowing Edges |  | {"edgeWidth":1..14=2,"edgeBrightness":0..20=6,"smoothness":1..15=5} | needs document; disabled in catalogue snapshot |
| `filter.gallery.grain` | Grain |  | {"intensity":0..100=40,"contrast":0..100=50,"grainType":"regular\|soft\|sprinkles\|clumped\|contrasty\|enlarged\|stippled\|horizontal\|vertical\|speckle","foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.graphicPen` | Graphic Pen |  | {"strokeLength":1..15=15,"lightDarkBalance":0..100=50,"strokeDirection":"rightDiagonal\|horizontal\|leftDiagonal\|vertical","foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.halftonePattern` | Halftone Pattern |  | {"size":1..12=1,"contrast":0..50=5,"patternType":"dot\|circle\|line","foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.inkOutlines` | Ink Outlines |  | {"strokeLength":1..50=4,"darkIntensity":0..50=20,"lightIntensity":0..50=10} | needs document; disabled in catalogue snapshot |
| `filter.gallery.mosaicTiles` | Mosaic Tiles |  | {"tileSize":2..100=12,"groutWidth":1..15=3,"lightenGrout":0..10=9} | needs document; disabled in catalogue snapshot |
| `filter.gallery.neonGlow` | Neon Glow |  | {"glowSize":-24..24=5,"glowBrightness":0..50=15,"glowColor":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.notePaper` | Note Paper |  | {"imageBalance":0..50=25,"graininess":0..20=10,"relief":0..25=11,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.oceanRipple` | Ocean Ripple |  | {"rippleSize":1..15=9,"rippleMagnitude":0..20=9} | needs document; disabled in catalogue snapshot |
| `filter.gallery.paintDaubs` | Paint Daubs |  | {"brushSize":1..50=8,"sharpness":0..40=7,"brushType":"simple\|lightRough\|darkRough\|wideSharp\|wideBlurry\|sparkle"} | needs document; disabled in catalogue snapshot |
| `filter.gallery.paletteKnife` | Palette Knife |  | {"strokeSize":1..50=25,"strokeDetail":1..3=3,"softness":0..10=0} | needs document; disabled in catalogue snapshot |
| `filter.gallery.patchwork` | Patchwork |  | {"squareSize":0..10=4,"relief":0..25=8} | needs document; disabled in catalogue snapshot |
| `filter.gallery.photocopy` | Photocopy |  | {"detail":1..24=7,"darkness":1..50=8,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.plaster` | Plaster |  | {"imageBalance":0..50=20,"smoothness":1..15=2,"light":"top\|topRight\|right\|bottomRight\|bottom\|bottomLeft\|left\|topLeft","foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.plasticWrap` | Plastic Wrap |  | {"highlightStrength":0..20=15,"detail":1..15=9,"smoothness":1..15=7} | needs document; disabled in catalogue snapshot |
| `filter.gallery.posterEdges` | Poster Edges |  | {"edgeThickness":0..10=2,"edgeIntensity":0..10=1,"posterization":0..6=2} | needs document; disabled in catalogue snapshot |
| `filter.gallery.reticulation` | Reticulation |  | {"density":0..50=12,"foregroundLevel":0..50=40,"backgroundLevel":0..50=5,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.roughPastels` | Rough Pastels |  | {"strokeLength":0..40=6,"strokeDetail":1..20=4,"texture":"canvas\|brick\|burlap\|sandstone","scaling":50..200=100,"relief":0..50=20,"light":"bottom\|bottomLeft\|left\|topLeft\|top\|topRight\|right\|b… | needs document; disabled in catalogue snapshot |
| `filter.gallery.smudgeStick` | Smudge Stick |  | {"strokeLength":0..10=2,"highlightArea":0..20=0,"intensity":0..10=10} | needs document; disabled in catalogue snapshot |
| `filter.gallery.spatter` | Spatter |  | {"sprayRadius":0..25=10,"smoothness":1..15=5} | needs document; disabled in catalogue snapshot |
| `filter.gallery.sponge` | Sponge |  | {"brushSize":0..10=2,"definition":0..25=12,"smoothness":1..15=5} | needs document; disabled in catalogue snapshot |
| `filter.gallery.sprayedStrokes` | Sprayed Strokes |  | {"strokeLength":0..20=12,"sprayRadius":0..25=7,"strokeDirection":"rightDiagonal\|horizontal\|leftDiagonal\|vertical"} | needs document; disabled in catalogue snapshot |
| `filter.gallery.stainedGlass` | Stained Glass |  | {"cellSize":2..50=10,"borderThickness":1..20=4,"lightIntensity":0..10=3,"foreground":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.stamp` | Stamp |  | {"lightDarkBalance":0..50=25,"smoothness":1..50=5,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.sumiE` | Sumi-e |  | {"strokeWidth":3..15=10,"strokePressure":0..15=2,"contrast":0..40=16} | needs document; disabled in catalogue snapshot |
| `filter.gallery.texturizer` | Texturizer |  | {"texture":"canvas\|brick\|burlap\|sandstone","scaling":50..200=100,"relief":0..50=4,"light":"top\|topRight\|right\|bottomRight\|bottom\|bottomLeft\|left\|topLeft","invert":bool} | needs document; disabled in catalogue snapshot |
| `filter.gallery.tornEdges` | Torn Edges |  | {"imageBalance":0..50=25,"smoothness":1..15=11,"contrast":1..25=17,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.gallery.underpainting` | Underpainting |  | {"brushSize":0..40=6,"textureCoverage":0..40=16,"texture":"canvas\|brick\|burlap\|sandstone","scaling":50..200=100,"relief":0..50=4,"light":"top\|topRight\|right\|bottomRight\|bottom\|bottomLeft\|le… | needs document; disabled in catalogue snapshot |
| `filter.gallery.waterPaper` | Water Paper |  | {"fiberLength":3..50=15,"brightness":0..100=60,"contrast":0..100=80} | needs document; disabled in catalogue snapshot |
| `filter.gallery.watercolor` | Watercolor |  | {"brushDetail":1..14=9,"shadowIntensity":0..10=1,"texture":1..3=1} | needs document; disabled in catalogue snapshot |
| `filter.lastFilter` | Last Filter | Filter | {} | needs document; disabled in catalogue snapshot |
| `filter.lensCorrection` | Lens Correction… | Filter | {"profile":"none\|auto\|generic","focalLength":mm=0,"correctDistortion":bool=true,"correctVignette":bool=true,"correctCA":bool=true,"autoScale":bool=false,"distortion":-100..100=0,"redCyan":-… | needs document; disabled in catalogue snapshot |
| `filter.liquify` | Liquify… | Filter | {"strokes":[{"tool":"forwardWarp\|reconstruct\|smooth\|twirlCw\|twirlCcw\|pucker\|bloat\|pushLeft\|freeze\|thaw\|lassoMask\|reconstructAll","size":px=100,"density":0-100=50,"pressure":0-100=100,"rate"… | needs document; disabled in catalogue snapshot |
| `filter.noise.addNoise` | Add Noise… | Filter > Noise | {"amount":0.1..400=12.5,"distribution":"uniform\|gaussian","monochromatic":bool,"seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.noise.despeckle` | Despeckle | Filter > Noise | {} | needs document; disabled in catalogue snapshot |
| `filter.noise.dustAndScratches` | Dust & Scratches… | Filter > Noise | {"radius":1..500=1,"threshold":0..255=0} | needs document; disabled in catalogue snapshot |
| `filter.noise.median` | Median… | Filter > Noise | {"radius":1..500=1} | needs document; disabled in catalogue snapshot |
| `filter.noise.reduceNoise` | Reduce Noise… | Filter > Noise | {"strength":0..10=6,"preserveDetails":0..100=60,"reduceColorNoise":0..100=45,"sharpenDetails":0..100=25,"removeJpegArtifact":bool} | needs document; disabled in catalogue snapshot |
| `filter.other.colorToAlpha` | Color to Alpha… | Filter > Other | {"color":color=#ffffff,"transparencyThreshold":0..1=0,"opacityThreshold":0..1=1} | needs document; disabled in catalogue snapshot |
| `filter.other.custom` | Custom… | Filter > Other | {"kernel":int[25],"scale":1..9999=1,"offset":-9999..9999=0} | needs document; disabled in catalogue snapshot |
| `filter.other.highPass` | High Pass… | Filter > Other | {"radius":0.1..1000=10} | needs document; disabled in catalogue snapshot |
| `filter.other.hsbHsl` | HSB/HSL | Filter > Other | {"inputMode":"rgb\|hsb\|hsl","rowOrder":"hsb\|hsl\|rgb"} | needs document; disabled in catalogue snapshot |
| `filter.other.maximum` | Maximum… | Filter > Other | {"radius":0.2..500=1,"preserve":"squareness\|roundness"} | needs document; disabled in catalogue snapshot |
| `filter.other.minimum` | Minimum… | Filter > Other | {"radius":0.2..500=1,"preserve":"squareness\|roundness"} | needs document; disabled in catalogue snapshot |
| `filter.other.offset` | Offset… | Filter > Other | {"horizontal":px=0,"vertical":px=0,"undefinedAreas":"wrap\|repeat\|transparent"} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.colorHalftone` | Color Halftone… | Filter > Pixelate | {"maxRadius":4..127=8,"channel1":-360..360=108,"channel2":-360..360=162,"channel3":-360..360=90,"channel4":-360..360=45} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.crystallize` | Crystallize… | Filter > Pixelate | {"cellSize":3..300=10,"seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.facet` | Facet | Filter > Pixelate | {} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.fragment` | Fragment | Filter > Pixelate | {} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.mezzotint` | Mezzotint… | Filter > Pixelate | {"type":"fineDots\|mediumDots\|grainyDots\|coarseDots\|shortLines\|mediumLines\|longLines\|shortStrokes\|mediumStrokes\|longStrokes","seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.mosaic` | Mosaic… | Filter > Pixelate | {"cellSize":2..200=10} | needs document; disabled in catalogue snapshot |
| `filter.pixelate.pointillize` | Pointillize… | Filter > Pixelate | {"cellSize":3..300=5,"seed":u32=0,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.render.clouds` | Clouds | Filter > Render | {"seed":u32=0,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.render.differenceClouds` | Difference Clouds | Filter > Render | {"seed":u32=0,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.render.fibers` | Fibers… | Filter > Render | {"variance":1..64=16,"strength":1..64=4,"seed":u32=0,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.render.flame` | Flame… | Filter > Render | {"flameType":"oneFlameAlongPath\|multipleFlamesAlongPath\|multipleFlamesPathDirections\|multipleFlamesVariousLength\|candleLight\|multipleFlamesOneDirection","length":1..1000=150,"randomizeLengt… | needs document; disabled in catalogue snapshot |
| `filter.render.lensFlare` | Lens Flare… | Filter > Render | {"brightness":10..300=100,"centerX":0..1=0.5,"centerY":0..1=0.5,"lens":"zoom\|prime35\|prime105\|moviePrime"} (normalized centre: 0..1 is the canvas; agents and actions may pass values outside… | needs document; disabled in catalogue snapshot |
| `filter.render.lightingEffects` | Lighting Effects… | Filter > Render | {"lightType":"spot\|point\|infinite","intensity":-100..100=75,"lightX":0..1=0.25,"lightY":0..1=0.2,"lightZ":0..2=0.6,"targetX":0..1=0.5,"targetY":0..1=0.55,"cone":1..89=45,"hotspot":0..100=50… | needs document; disabled in catalogue snapshot |
| `filter.render.pictureFrame` | Picture Frame… | Filter > Render | {"frame":"vineWithFlowers\|vineWithLeaves\|ivy\|roses\|daisies\|berries\|bamboo\|waves\|zigzag\|dots\|rope\|scallops\|doubleLine\|snowflakes\|stars\|hearts","margin":0..30=4,"size":1..100=50,"arrangement"… | needs document; disabled in catalogue snapshot |
| `filter.render.relight` | Relight… | Filter > Render | {"angle":-180..180=45,"elevation":0..90=40,"intensity":0..100=40,"ambient":0..100=55,"warmth":-100..100=0,"softness":1..100=25} | needs document; disabled in catalogue snapshot |
| `filter.render.tree` | Tree… | Filter > Render | {"baseTreeType":1..34=1,"lightDirection":1..5=3,"leavesAmount":0..100=50,"leavesSize":0..200=100,"branchesHeight":50..300=100,"branchesThickness":50..200=100,"defaultLeaves":bool=true,"leav… | needs document; disabled in catalogue snapshot |
| `filter.sharpen.sharpen` | Sharpen | Filter > Sharpen | {} | needs document; disabled in catalogue snapshot |
| `filter.sharpen.sharpenEdges` | Sharpen Edges | Filter > Sharpen | {} | needs document; disabled in catalogue snapshot |
| `filter.sharpen.sharpenMore` | Sharpen More | Filter > Sharpen | {} | needs document; disabled in catalogue snapshot |
| `filter.sharpen.smartSharpen` | Smart Sharpen… | Filter > Sharpen | {"amount":1..500=100,"radius":0.1..64=1,"reduceNoise":0..100=10} | needs document; disabled in catalogue snapshot |
| `filter.sharpen.unsharpMask` | Unsharp Mask… | Filter > Sharpen | {"amount":1..500=50,"radius":0.1..1000=1,"threshold":0..255=0} | needs document; disabled in catalogue snapshot |
| `filter.stylize.diffuse` | Diffuse… | Filter > Stylize | {"mode":"normal\|darkenOnly\|lightenOnly\|anisotropic","seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.stylize.emboss` | Emboss… | Filter > Stylize | {"angle":-180..180=135,"height":1..100=3,"amount":1..500=100} | needs document; disabled in catalogue snapshot |
| `filter.stylize.extrude` | Extrude… | Filter > Stylize | {"type":"blocks\|pyramids","size":2..255=30,"depth":1..255=30,"depthMode":"random\|levelBased","solidFrontFaces":bool,"maskIncompleteBlocks":bool,"seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.stylize.findEdges` | Find Edges | Filter > Stylize | {} | needs document; disabled in catalogue snapshot |
| `filter.stylize.oilPaint` | Oil Paint… | Filter > Stylize | {"stylization":0.1..10=4,"cleanliness":0..10=5,"scale":0.1..10=1,"bristleDetail":0..10=5,"lighting":bool=true,"angle":-180..180=-60,"shine":0..10=1} | needs document; disabled in catalogue snapshot |
| `filter.stylize.solarize` | Solarize | Filter > Stylize | {} | needs document; disabled in catalogue snapshot |
| `filter.stylize.tiles` | Tiles… | Filter > Stylize | {"count":1..99=10,"maxOffset":1..99=10,"fill":"background\|foreground\|inverse\|unaltered","seed":u32=0,"foreground":json,"background":json} | needs document; disabled in catalogue snapshot |
| `filter.stylize.traceContour` | Trace Contour… | Filter > Stylize | {"level":0..255=128,"edge":"lower\|upper"} | needs document; disabled in catalogue snapshot |
| `filter.stylize.wind` | Wind… | Filter > Stylize | {"method":"wind\|blast\|stagger","direction":"fromRight\|fromLeft","seed":u32=0} | needs document; disabled in catalogue snapshot |
| `filter.vanishingPoint` | Vanishing Point… | Filter | {"planes":[{"corners":[[x,y]×4]} \| {"from":plane,"edge":"top\|right\|bottom\|left","angle":deg=90,"depth":1}],"focalLength":px=0,"paste":[{"plane":0,"layer":id? (else the clipboard),"at":[u,v]… | needs document; disabled in catalogue snapshot |
| `filter.video.deInterlace` | De-Interlace… | Filter > Video | {"eliminate":"oddFields\|evenFields","createBy":"interpolation\|duplication"} | needs document; disabled in catalogue snapshot |
| `filter.video.ntscColors` | NTSC Colors | Filter > Video | {} | needs document; disabled in catalogue snapshot |

## `style` (7)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `style.presets.apply` | Apply Style |  | {"preset":name,"group":name?,"layers":[ids]?\|"layer":id? (default: the selected layers),"add":bool=false (⇧-click: add to the existing effects)} → {layers,style} | needs document; disabled in catalogue snapshot |
| `style.presets.edit` | Edit Style Presets |  | {"action":"rename\|delete\|move\|newGroup\|renameGroup\|deleteGroup","preset":name\|[names] (rename/delete/move),"group":name? (narrows the lookup; the group for renameGroup/deleteGroup),"name":s… |  |
| `style.presets.exportAsl` | Export Styles… |  | {"group":name? (only that group),"styles":[names]? (only these),"path":".asl file"? (else the bytes come back as base64 `data`)} → {count, bytes, patterns, warnings, path\|data} |  |
| `style.presets.importAsl` | Import Styles… |  | {"path":".asl file"?,"data":base64 bytes?,"group":string?=file name (a built-in group's name becomes "<name> 2": built-ins are never replaced),"replace":bool=true (replace a group of the sa… |  |
| `style.presets.list` | Style Presets |  | {} → {groups:[{name,presets:[{name,effects,blend,fillOpacity,opacity}]}]} |  |
| `style.presets.new` | New Style… |  | {"name":str="Style","group":name?,"layer":id?,"includeEffects":bool=true,"includeBlending":bool=true,"effects":[[kind, params]]? (explicit list, e.g. the Layer Style dialog's pending state;… | needs document; disabled in catalogue snapshot |
| `style.presets.reset` | Restore Default Styles |  | {"append":bool=false} |  |
