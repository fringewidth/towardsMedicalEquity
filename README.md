# Towards Medical Equity

## Goals:

### Project Technical Goals: A Roadmap

#### Phase 1: Data Collection

- [x] **Identify Hospital Dataset**: Locate a dataset with comprehensive information on hospitals across India.
- [x] **Extract and Filter Relevant Data**: Extract necessary information (e.g., hospital names) and filter out irrelevant values.
- [x] **Web Scraping Setup**: Develop and test a script to scrape data (coordinates, ratings, number of ratings) from Google Maps for each hospital.
- [x] **Data Documentation**: Document scraped data, including coordinates, ratings, and review counts.

#### Phase 2: Calculate Effective Rating and Sphere of Influence

- [x] **Define Effective Rating Formula**: Implement a formula combining ratings and review counts to calculate an effective rating.
- [ ] **Determine Sphere of Influence**: Develop an algorithm to calculate influence radius based on each hospital's effective rating.

#### Phase 3: Grid Overlay and Influence Calculation

- [ ] **Grid the Country**: Create a 1 km² grid overlay for India.
- [ ] **Get Census Data**: Devise a means to use census data for the project
- [ ] **Calculate Influence Per Cell**: Sum influence scores from each hospital within the radius of each cell, and multiply by census data for population density.

#### Phase 4: Identify Low-Access Areas

- [ ] **Define Low-Access Thresholds**: Establish thresholds to classify cells as “low-access” based on influence scores.
- [ ] **Visualize Low-Access Areas**: Use mapping libraries to create a visual representation of underserved areas.

#### Phase 5: Anonymization of Sensitive Data

- [ ] **Define Anonymization Techniques**: Select appropriate anonymization techniques for hospital ratings and coordinates.
- [ ] **Test Cluster Consistency Post-Anonymization**: Re-apply clustering to anonymized data and compare results with original clusters.

#### Phase 6: Documentation and Publication

- [ ] **Document Anonymization Methodology**: Publish a clear guide on anonymization techniques that maintain data utility.
- [ ] **Prepare Final Report and Visualizations**: Summarize findings and create visualizations of influence distribution and underserved areas.

## Methodology:

#### 1. Defining Effective Rating and Sphere of Influence

- **Effective Rating**: Create a formula that combines the rating (1–5 scale) and the number of ratings to balance quality and popularity. For example:
- **Effective Rating**: Create a formula that combines the rating (1–5 scale) and the number of ratings to balance quality and popularity. For example:
  ```
  Effective Rating = Rating * log(1 + Number of Ratings)
  ```
- **Sphere of Influence**: Define the influence radius using an exponential decay function:
  ```
  Radius = R0 * exp(alpha * Effective Rating)
  ```
  where `R0` is a base radius, and `alpha` is a factor controlling the decay rate.

#### 2. Influence Calculation per Square Kilometer

- Overlay a grid over the country (e.g., each cell representing 1 km²).
- For each hospital, calculate its influence within each cell inside its radius, then sum influences from all hospitals at each cell.
- Multiply the influence value for each cell by its population density (using census data) to highlight underserved areas.

#### 3. Identifying Low-Access Areas

- Define thresholds to identify “low-access” areas based on influence scores (e.g., bottom quartile).
- Visualize these areas on a map to identify patterns, especially in rural or densely populated areas.

#### 4. Anonymization to Preserve Influence Consistency

- **Coordinates**: Apply slight perturbations within a tolerance that doesn’t significantly impact proximity-based influence.
- **Effective Rating**: Implement generalization or value swapping within a defined range so that ratings maintain influence while masking original values.
- Ensure the anonymization process preserves the distribution and relative influence of each hospital.

#### 5. Documentation of Anonymization Techniques

- Document methods to replicate the anonymization process while ensuring data utility.
- Demonstrate consistency between anonymized and original data’s influence maps, ensuring accuracy for public sharing.
