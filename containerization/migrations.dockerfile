# vi: set ft=dockerfile :



FROM decapod-base-plugins
MAINTAINER Sergey Arkhipov <sarkhipov@mirantis.com>


LABEL description="Migration script for Decapod" version="0.2.0" vendor="Mirantis"


COPY output/eggs /eggs


RUN set -x \
  && apt-get update \
  && apt-get install -y --no-install-recommends \
      gcc \
      libffi-dev \
      python3-dev \
      python3-pip \
  && pip3 install --compile --no-cache-dir --disable-pip-version-check \
      decapod_migrations*.whl \
      decapod_api*.whl \
      decapod_controller*.whl \
      decapod_controller*.whl \
  && rm -r /eggs \
  && apt-get clean \
  && apt-get purge -y libffi-dev python3-pip python3-dev gcc \
  && apt-get autoremove -y \
  && rm -r /var/lib/apt/lists/*


ENTRYPOINT ["dockerize", "-wait", "tcp://database:27017", "--", "decapod-migrations"]
CMD ["apply"]
