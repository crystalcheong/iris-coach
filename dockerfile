# ==============================================================================
# Build stage

ARG IMAGE=intersystemsdc/iris-community:latest
FROM $IMAGE

WORKDIR /irisdev/app

# Define args for environment variables
ARG IRISUSERNAME
ARG IRISPASSWORD
ARG IRISNAMESPACE

# Set environment variables from args
ENV IRISUSERNAME=${IRISUSERNAME}
ENV IRISPASSWORD=${IRISPASSWORD}
ENV IRISNAMESPACE=${IRISNAMESPACE}

ENV PYTHON_PATH=/usr/irissys/bin/
ENV LD_LIBRARY_PATH=${ISC_PACKAGE_INSTALLDIR}/bin:${LD_LIBRARY_PATH}

ENV PATH "/home/irisowner/.local/bin:/usr/irissys/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/home/irisowner/bin"

COPY . .

# Update pip, setuptools, and wheel
RUN pip3 install --upgrade pip setuptools wheel

# Clear pip cache
RUN pip3 cache purge

# Install the required Python packages
RUN pip3 install -r requirements.txt --verbose

# ==============================================================================
# Production stage

ENV INIT_PATH=./init.sh
# Copy the init script and make it executable
COPY init.sh $INIT_PATH
# Switch to root to change permissions
USER root
RUN chmod +x $INIT_PATH

# Switch back to the original user
USER irisowner

# Set the entrypoint to the init.sh script
ENTRYPOINT ["sh", "-c", "$INIT_PATH"]