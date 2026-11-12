![Intro scenery: the checker's hand lifting one amber bottle from its row and holding it toward the light, a blank green tag hanging from its neck by string, while his other hand holds a board of blurred handwritten lines and tick marks](intro-banner.png)

# analyze-code-dependency-scanner

![Wordmark banner: tall pine shelves packed with amber bottles in exact rows filling a stock room, a checker standing on a short ladder writing on a board, one bottle near him carrying a pale green tag while the rest stand unmarked](banner.png)

<p align="center"><img src="logo.png" alt="analyze-code-dependency-scanner logo: one amber bottle straight on at the centre of a pine shelf, its cream label band left blank and a green checkmark tag tied at its neck, rows of matching labelled bottles softening behind it" width="200"></p>

![Animated themed scene](scene.svg)

Lists the dependencies a repository declares and checks them against a small built in example table only: requests at 2.28.0 and django at 3.2.0, the two entries in main.py. It does not query public vulnerability databases and does not check whether packages are outdated, so a result with no flags only means no declared package matched those two entries. - Focused on Data analysis and reporting

## Install
`git clone https://github.com/ShadowGuardAI/analyze-code-dependency-scanner`


![Minor divider](sep-light.svg)

## Usage
`./analyze-code-dependency-scanner [params]`


![Major divider](sep-heavy.svg)

## Parameters
- `-h`: Show help message and exit
- `-o`: No description provided
- `-f`: Output format: csv or json. Defaults to csv.
- `-p`: No description provided
- `--ignore-vulnerabilities`: Path to a JSON file containing a list of vulnerabilities to ignore.


![Minor divider](sep-light.svg)

## License
Copyright (c) ShadowGuardAI

> Basket note: this scanner does not query public vulnerability databases and does not check whether packages are outdated. No flags means only that no declared package matched requests at 2.28.0 or django at 3.2.0.
> Basket note: the parameters -o and -p arrive with no description provided, and they are printed that way here rather than given a guessed job.
