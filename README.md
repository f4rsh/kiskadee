# kiskadee

kiskadee is a continuous static analysis tool which writes the analysis
results into a
[firehose](https://github.com/fedora-static-analysis/firehose)
database.

## Documentation

For more information on the project, installation or development
environment setup, refer to the full [kiskadee
documentation](https://docs.pagure.org/kiskadee).

There is an academic paper describing our work torwards ranking static analysis
warnings, available
[here](https://link.springer.com/chapter/10.1007/978-3-319-92375-8_8).

To build the documentation locally:

	pip install -U sphinx sphinx\_rtd\_theme
	cd doc
	make html

Open the index.html file, inside the _build/html directory.

## Repositories

kiskadee core and API development are hosted at [pagure](https://pagure.io/kiskadee).

kiskadee frontend is hosted at [pagure](https://pagure.io/kiskadee/kiskadee_ui).

We maintain mirrors on [gitlab](https://gitlab.com/kiskadee/kiskadee)
and [github](https://github.com/LSS-USP/kiskadee) since earlier
development used both at some point for CI purposes. **Do not open
issues or pull requests on these mirrors**.

kiskadee have a CI environment hosted at this
[url](http://143.107.45.126:30130/blue/organizations/jenkins/LSS-USP%2Fkiskadee/activity).

## Ranking experiments

Data and information on ranking experiments for kiskadee's ranking module are
available [here](https://gitlab.com/ccsl-usp/kiskadee-ranking-data).

## Communication

Join us on IRC: #kiskadee @ freenode

Mailing list: `kiskadee@googlegroups.com`

You can subscribe to our mailing lists by sending an email to
`kiskadee+subscribe@googlegroups.com`.

## License
Copyright (C) 2017 the AUTHORS (see the AUTHORS file)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
