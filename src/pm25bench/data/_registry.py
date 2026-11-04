"""Hashes SHA-256 dos arquivos de dados nos commits fixados (gerado automaticamente)."""

#: Arquivos anuais da reanálise do SISAM (ZIP) no repositório de dados de treino.
SISAM_REGISTRY: dict[str, str] = {
    "sisam_municipio_reanalise_diario_2010-01-01_2010-12-31.zip": "sha256:3e3a5258f2f1d12fa7f25ccf01eb9b06217a1d97972b070350cdddc9f2d15590",
    "sisam_municipio_reanalise_diario_2011-01-01_2011-12-31.zip": "sha256:c02ddeaf173a53a4184e974df496a21050f82f09fe2427f63b6e177a6c2f3055",
    "sisam_municipio_reanalise_diario_2012-01-01_2012-12-31.zip": "sha256:c0161d2c5204a2098efcb45ce00f4b63572e43cddcc070c30f6dac482450550f",
    "sisam_municipio_reanalise_diario_2013-01-01_2013-12-31.zip": "sha256:8aadfd03a25939e6e7132f276e3f51d90039001a02b66a6f096b6019d263fe76",
    "sisam_municipio_reanalise_diario_2014-01-01_2014-12-31.zip": "sha256:e031407f946e9f193d3a3e65e2412bd6aa38f42b3704b90f7a4177ff814387b4",
    "sisam_municipio_reanalise_diario_2015-01-01_2015-12-31.zip": "sha256:1c1d972b824b2092386752370185ea5eb4e388f78f5dae6a2bd55783b1f9b6eb",
    "sisam_municipio_reanalise_diario_2016-01-01_2016-12-31.zip": "sha256:c69f3b153ea1e527777b2689b64e8380bd857252ce996b3995fdd91ba70524d0",
    "sisam_municipio_reanalise_diario_2017-01-01_2017-12-31.zip": "sha256:71641c0ae4c24c67716f8538ef17fa634e1e4bc386eb0861b0d75a25f0e42034",
    "sisam_municipio_reanalise_diario_2018-01-01_2018-12-31.zip": "sha256:714e9e02a720f529df3dc2120c75130bf4523d6d5b4795d1472665ecbf87e98a",
    "sisam_municipio_reanalise_diario_2019-01-01_2019-12-31.zip": "sha256:90cfb865e729849e8298b010971e9e5dd350436d20e18109ddd51b76abe2a70c",
    "sisam_municipio_reanalise_diario_2020-01-01_2020-12-31.zip": "sha256:335c95d0069a1d5df9d6ab4cf857c63b2291d83e818747d21299ebb9b5a95045",
    "sisam_municipio_reanalise_diario_2021-01-01_2021-12-31.zip": "sha256:d27c4c29f8750c5df2432db7639df36a8cecae3d4775ef477c59020cb330dbd7",
    "sisam_municipio_reanalise_diario_2022-01-01_2022-12-31.zip": "sha256:05262fbc8b1ed52170fbf93e79ff027494f2a3cad32f12f3a7754c519a28150c",
    "sisam_municipio_reanalise_diario_2023-01-01_2023-12-31.zip": "sha256:a3eb1d071df7fd4a01dce8bb96634891e2c0ee4398530e0dd8a7889bb58f8e4e",
    "sisam_municipio_reanalise_diario_2024-01-01_2024-12-31.zip": "sha256:59b7e980dc6f8731ea7580b5f7172c5242e4c8da0a19126661b5cb07ba08c493",
}

#: Hashes dos arquivos da estação 73 (Congonhas) no commit fixado.
CETESB_REGISTRY: dict[str, str] = {
    "73/2008.csv": "sha256:31605ac71d75211b2b780dd4612873d646ac80dfed271db208ebc1a16d5d1dea",
    "73/2009.csv": "sha256:31605ac71d75211b2b780dd4612873d646ac80dfed271db208ebc1a16d5d1dea",
    "73/2010.csv": "sha256:31605ac71d75211b2b780dd4612873d646ac80dfed271db208ebc1a16d5d1dea",
    "73/2011.csv": "sha256:6649c9ed734a1789126ee93032a0d228eaa85c3bbada0afeb00234ef2645723c",
    "73/2012.csv": "sha256:c4d7492161398c97b24b1fd4b1e348c00ee7eafe37f3b2614d1e33d9943ccd73",
    "73/2013.csv": "sha256:938117a170bda0c7185fe7578bfb54ef42429fefa4e2550cd75bdaaa56d8bb6c",
    "73/2014.csv": "sha256:46527dfaf58640703467c344b3949b19d89673a0c109d35bd281e3fccd1ff2dd",
    "73/2015.csv": "sha256:6007854af22c3183552bf35983f32f1472f745e6473ffbcd43008f445cf406c2",
    "73/2016.csv": "sha256:41df9f60ae856d0c17c1b9ad1e8d159399314ef350aaed503fbb2e29dbf4b560",
    "73/2017.csv": "sha256:c21badf4ef5b585d0d7010c5b28f76ec6b591393fe8fa08b1fb31ed7408fa152",
    "73/2018.csv": "sha256:7d4d99b9a68d3182ef12a30564ca85b17fc545fb2bc9c4ce004dc971b827d26e",
    "73/2019.csv": "sha256:852389dfd75db5db8d93a367bf6a9512f0a7e34ea253975ab81b6a55bbaf4a0d",
    "73/2020.csv": "sha256:d92ed98a8052400dd42874c86741355637b119245ceebe66f577b218eec3e92d",
    "73/2021.csv": "sha256:64190fe2e3f8e0c7d4b5e4c61a7a4bd7adc3fa0f52ea7cc7eb9404d9e6a64086",
    "73/2022.csv": "sha256:63e712e39f105a0f6d0059b24d4e32a871a92ab352cc1b9c61967f4019304ef5",
    "73/2023.csv": "sha256:1fef0da32be1c4cb71cbc80e5da4d73ddcab481b9ef30c8cbfbcc42c89769f5c",
    "73/2024.csv": "sha256:cb31bf856575d67aac8c38ecef37e053b78aa7abc20a6c978e267a738862461a",
    "73/2025.csv": "sha256:4cb82692dd784b9bc5281c6d77b82c1d1596f9f053cd1ad3dc93cacc61e1e0e7",
    "73/2026.csv": "sha256:3a6ad737a96498c8b033596f124b743bb94a660ef6e852ae58ee80230d62fab3",
}
