#!/bin/bash

# Copyright (C) 2019-2020 Vanessa Sochat.

# This Source Code Form is subject to the terms of the
# Mozilla Public License, v. 2.0. If a copy of the MPL was not distributed
# with this file, You can obtain one at http://mozilla.org/MPL/2.0/.

# AskCI CLI script.

SCRIPTNAME="askci.sh";
SCRIPTPATH=$(realpath $0);
SCRIPTDIR=$(dirname $SCRIPTPATH);

IN_RED="\033[0;31m";
IN_GRY="\033[0;44m";
IN_DEF="\033[0m";

# Generates a random string of desired length.
#   e.g.
#     random-string 16
function random-string {
    cat /dev/urandom | tr -dc 'a-zA-Z0-9!@#$%^&*()_+-=><?[]{}' | fold -w ${1:-32} | head -n 1
}

# Ask a yes/no question for confirmation.
function read_yes_no {
    printf "${IN_RED}[y|n] ${IN_DEF}";
    read yesno;
    while [[ "${yesno}" != "y" && "${yesno}" != "n" ]]
    do
        printf "${IN_RED}please answer [y|n] ${IN_DEF}";
        read yesno;
    done

    if [[ "${yesno}" == "n" ]]; then
        return 1;
    else
        return 0;
    fi
}

# Prints a message if AskCI is not installed.
function alert_if_not_installed {
    if ! is_installed; then
        echo;
        printf "${IN_GRY}.=----------------------------------------------=.\n";
        printf           "|                  AskCI CLI                     |\n";
        printf           ".=----------------------------------------------=.${IN_DEF}";
        echo;
        echo "  Apparently you haven't installed AskCI";
        echo "    or your environment variables are tampered.";
        echo "  Please run './askci.sh' to get started.";
        echo;
        exit 1;
    fi
}

# Prints a list of commands with their description.
function script_help {
    printf "${IN_GRY}.=----------------------------------------------=.\n";
    printf           "|                  AskCI CLI                     |\n";
    printf           "|             Available Instructions             |\n";
    printf           ".=----------------------------------------------=.${IN_DEF}\n";
    echo;
    printf "${IN_RED}dev${IN_DEF}\n";
    echo "  Starts development containers."; echo;
    printf "${IN_RED}prod${IN_DEF}\n";
    echo "  Starts production stack."; echo;
    printf "${IN_RED}stop <prod|dev>${IN_DEF}\n";
    echo "  Stops containers."; echo;
    printf "${IN_RED}rm <prod|dev>${IN_DEF}\n";
    echo "  Remove containers."; echo;
    printf "${IN_RED}up <prod|dev>${IN_DEF}\n";
    echo "  Just brings up the containers. no building."; echo;
    printf "${IN_RED}restart <prod|dev>${IN_DEF}\n";
    echo "  Restart containers."; echo;
    printf "${IN_RED}logs <prod|dev>${IN_DEF}\n";
    echo "  View logs."; echo;
    printf "${IN_RED}uninstall${IN_DEF}\n";
    echo "  Removes all the content and containers related to AskCI."; echo;
}

# Prompts user to input something with a message and an example
#   and puts the result in the given variable.
#
#     e.g.
#       prompt_user "log storage path" "(e.g. /path/to/smthing)" OUTPUT
function prompt_user {
    WHAT="$1";
    EXAMPLE="$2";
    OUTPUT_VAR="$3";
    ASKED_VAR="";
    while [ "$ASKED_VAR" == "" ]; do
        read -p "Enter $WHAT $EXAMPLE: " -e ASKED_VAR;
        if [[ "$ASKED_VAR" != "" ]]; then
            printf "${IN_RED}Do you confirm $ASKED_VAR for $WHAT? ${IN_DEF}";
            if ! read_yes_no; then
                ASKED_VAR="";
            fi
        fi
    done
    export "$OUTPUT_VAR"="$ASKED_VAR";
    echo;
}

# Returns state 0 if askci is installed else 1.
function is_installed {
    if [ -f "$SCRIPTDIR/.env" ]; then
        source "$SCRIPTDIR/.env";
        if [[ "$INSTALLED_IN" =~ ^[0-9]{10,11}$ ]]; then
            return 0;
        fi
    fi

    return 1;
}

# Initializes required environment variables.
function setup {
    if ! is_installed; then
        if [ -f "$SCRIPTDIR/.env" ]; then
            rm "$SCRIPTDIR/.env";
        fi
        touch "$SCRIPTDIR/.env";
        printf "${IN_GRY}.=----------------------------------------------=.\n";
        printf          "|                  AskCI CLI                     |\n";
        printf          "|   Welcome to the setup process for AskCI!      |\n";
        printf          "|      This won't take more than a minute.       |\n";
        printf          ".=----------------------------------------------=.${IN_DEF}\n";
        ask_for_envs;
        echo "INSTALLED_IN=$(date +%s)" >>  "$SCRIPTDIR/.env";
    fi
}

# Generates a random string and puts in environment variables
#   to be used in ASKCIango settings.
function put_secret_key {
    echo "ASKCI_KEY='$(random-string 40)'" >> "$SCRIPTDIR/.env";
}

# Prompts user to enter required environment variables
#   for askci to start.
function ask_for_envs {
    echo;
    echo "Asking for host details :->"; echo;
    ask_for_hostname;
    echo "Asking for server details:->";echo;
    ask_for_configs;
    printf "Generating a secret for you... ";
    put_secret_key;
    printf "done \xE2\x9C\x94 \n";
    echo ">>> (We'are all set and ready to go.) <<<";
    echo;
}

# Asks user for host IP address and domain name.
function ask_for_hostname {
    prompt_user "your host IP address" "(e.g. 173.194.122.231)" ASKCIHIPADDR;
    prompt_user "your host domain name" "(e.g. google.com)" ASKCIHDOMNN;
    echo "ASKCI_HOSTS=['$ASKCIHIPADDR','$ASKCIHDOMNN']" >> "$SCRIPTDIR/.env";
}

# As user for variables that are put in configuration
function ask_for_configs {
    prompt_user "a help contact email for your server" "(e.g., name@institution.edu)" HELP_CONTACT_EMAIL;
    prompt_user "an institutional help or support site" "(e.g., https://srcc.stanford.edu)" HELP_INSTITUTION_SITE;
    prompt_user "your institution or affiliation " "(e.g., Stanford University)" NODE_INSTITUTION;
    prompt_user "a lowercase (no spaces) unique resource identifier for the server " "(e.g., askci-server)" NODE_URI;
    prompt_user "the name of the server " "(e.g., AskCI)" NODE_NAME;
    prompt_user "a Twitter account " "(e.g., askcyberinfra)" NODE_TWITTER;
    echo "HELP_CONTACT_EMAIL=\"$HELP_CONTACT_EMAIL\"" >> "$SCRIPTDIR/.env";
    echo "HELP_INSTITUTION_SITE=\"$HELP_INSTITUTION_SITE\"" >> "$SCRIPTDIR/.env";
    echo "NODE_INSTITUTION=\"$NODE_INSTITUTION\"" >> "$SCRIPTDIR/.env";
    echo "NODE_URI=\"$NODE_URI\"" >> "$SCRIPTDIR/.env";
    echo "NODE_NAME=\"$NODE_NAME\"" >> "$SCRIPTDIR/.env";
    echo "NODE_TWITTER=\"$NODE_TWITTER\"" >> "$SCRIPTDIR/.env";
}


# Starts development Docker containers.
function dev {
    setup;
    docker-compose build;
    docker-compose up -d;
}

# Starts production stack.
function prod {
    setup;
    docker-compose -f https/docker-compose.yml build;
    docker-compose -f https/docker-compose.yml up -d;
}

# Just brings up the containers. no building.
function bring_up {
    setup;
    if [[ "$1" == "dev" ]]; then
        docker-compose up -d;
    elif [[ "$1" == "prod" ]]; then
        docker-compose -f https/docker-compose.yml up -d;
    fi
}

# Run a compose command (logs, restart, stop, rm)
function compose_command {
    level="${1}";
    command="${2}";
    shift; shift;
    if [[ "${level}" == "dev" ]]; then
        docker-compose "${command}" "${@}";
    elif [[ "${level}" == "prod" ]]; then
        docker-compose -f https/docker-compose.yml "${command}" "${@}";
    fi
}

# Removes environment variables, folders and Docker containers.
function uninstall {
    printf "${IN_GRY}This will remove all your files:\n";
    printf "  - Installed environment variables\n";
    printf "  - Entered folders for database, deposit, medias, etc\n";
    printf "  - Docker containers and images\n";
    printf "  - All your log and pid files${IN_DEF}\n";
    printf "${IN_RED}Do you confirm?";

    if read_yes_no; then
        source "$SCRIPTDIR/.env";
        sudo rm -rf "$DB_FOLDER" "$DEPOSIT_FOLDER" "$STATIC_FOLDER" "$MEDIA_FOLDER";
        stop;
        rm_dev;
        rm_dev_image;
        rm_prod;
        rm_prod_image;
        sudo find "$SCRIPTDIR" -name "*.log" -delete;
        sudo find "$SCRIPTDIR" -name "*.pid" -delete;
        rm "$SCRIPTDIR/.env";
        printf "Uninstalled AskCI.\n";
    else
        printf "Uninstallation aborted.\n";
    fi
}

# Let's see what user wants.
if [[ "$1" == "dev" ]]; then
    dev;
elif [[ "$1" == "prod" ]]; then
    prod;
elif [[ "$1" == "up" ]]; then
    if [[ "$2" == "prod" || "$2" == "dev" ]]; then
        bring_up $2 $3;
    else
        echo "You should type in 'prod' or 'dev' after the up command.";
    fi
elif [[ "$1" == "restart" || "$1" == "stop" || "$1" == "logs" || "$1" == "rm" ]]; then
    if [[ "$2" == "prod" || "$2" == "dev" ]]; then
        command="${1}"
        level="${2}"
        shift; shift;
        compose_command "${level}" "${command}" "${@}";
    else
        echo "You should type in 'prod' or 'dev' after the command.";
    fi
elif [[ "$1" == "uninstall" ]]; then
    uninstall;
else
    script_help;
fi
