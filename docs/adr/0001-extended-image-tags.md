# Extended Image tags

Extended Images use the Upstream n8n Version as their initial immutable Docker and git tag, while corrected republishes for the same upstream version add an explicit repository-local Extended Image Revision such as `-r1`. Keeping the revision separate allows the parent `n8nio/n8n` image and matching `n8nio/runners` image to retain the real upstream version; the mutable `latest` Docker tag remains available for existing consumers.
